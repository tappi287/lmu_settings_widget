import logging
import time
from typing import Any, List, Optional

import gevent

from .app_settings import AppSettings
from .directInputKeySend import PressReleaseKey, PressKey, ReleaseKey
from .rf2connect import RfactorState, RfactorConnect
from .rf2events import RfactorStatusEvent, RfactorLiveEvent, RfactorQuitEvent, RecordBenchmarkEvent
from .utils import AppAudioFx

"""
    Le Mans Ultimate: localhost:6397/swagger/index.html
"""


class CommandUrls:
    series = "/rest/race/series"

    @classmethod
    def set_series_args(cls, series_id: str):
        if AppSettings.last_rf_version >= "1.1125":
            # -- new Protocol from v1125
            return {"url": f"{cls.series}?signature={series_id}"}
        else:
            # -- previous versions
            return {"url": cls.series, "data": series_id}


class Command:
    """A command to be held in the CommandQueue and to be send to rF2 if it is in the desired state"""

    wait_for_state = 0
    play_replay = 1
    nav_action = 2
    quit = 3
    get_content = 4
    set_content = 5
    start_race = 6
    drive = 7
    press_key = 8
    press_shift_key = 9
    press_ctrl_key = 10
    press_alt_key = 11
    timeout_command = 12
    record_benchmark = 13
    set_session_settings = 14
    replay_playback = 15
    replay_time = 16
    replay_focus = 17
    ai_take_control = 18
    to_race_menu = 19

    names = {
        0: "wait_for_state",
        1: "play_replay",
        2: "nav_action",
        3: "quit",
        4: "get_content",
        5: "set_content",
        6: "start_race",
        7: "drive",
        8: "press_key",
        9: "press_shift_key",
        10: "press_ctrl_key",
        11: "press_alt_key",
        12: "timeout_command",
        13: "record_benchmark",
        14: "set_session_settings",
        15: "replay_playback",
        16: "replay_time",
        17: "replay_focus",
        18: "ai_take_control",
        19: "to_race_menu",
    }

    default_timeout = 480.0  # Seconds

    def __init__(self, command: int, data: Any = None, timeout: float = None):
        self.command = command
        self.data = data
        self.timeout = timeout or self.default_timeout

        self.finished = False
        self.reset_queue = False
        self.created = time.time()

        self.method = getattr(self, f"{self.names.get(command)}_method")

    def execute(self):
        if callable(self.method):
            self.method()
        else:
            logging.error(
                "Could not find method to execute for command: %s %s", self.command, self.names.get(self.command)
            )

    def activate(self):
        self.created = time.time()
        logging.debug("rFactor command activated: %s, Timeout: %s", Command.names.get(self.command), self.timeout)

    @property
    def timed_out(self) -> bool:
        result = False
        if (time.time() - self.created) > self.timeout:
            result = True

        if result:
            logging.info("Rfactor Command timed out: %s", Command.names.get(self.command))

        return result

    @staticmethod
    def _get_all_tracks_cars_series(selected):
        for series in AppSettings.content.get("series", list()):
            if series and series.get("shortName") == "All Tracks & Cars":
                if AppSettings.last_rf_version >= "1.1125" and series.get("signature", None):
                    selected["series"] = series.get("signature")
                elif series.get("id"):
                    selected["series"] = series.get("id")
                break
        return selected

    @staticmethod
    def _check_request(r) -> bool:
        if r and r.status_code in (200, 201, 202, 203, 204):
            return True
        return False

    def wait_for_state_method(self):
        if self.data == RfactorConnect.state:
            logging.debug("Found desired command state: %s", RfactorState.names.get(self.data))
            self.finished = True
        RfactorStatusEvent.set(f"Waiting for state: {RfactorState.names.get(self.data)}")

    def quit_method(self):
        logging.debug("Executing command quit rF2.")
        RfactorStatusEvent.set("Sending quit event to WebUI")
        quit_result = RfactorConnect.quit()
        RfactorQuitEvent.quit_result.set(quit_result)

        if quit_result:
            self.finished = True

    def play_replay_method(self) -> bool:
        is_playing_replay = False

        if not self.data:
            logging.error("Can not play replay without name!")
            return False

        RfactorStatusEvent.set(f"Getting Replay Id: {self.data}")

        # RfactorConnect.wait_for_rf2_ui(20.0)
        replays = RfactorConnect.get_replays()
        gevent.sleep(0.1)

        for r in replays:
            if r.get("replayName", "") == self.data:
                logging.debug("Matched Web UI replay with requested replay id: %s", r.get("id"))
                RfactorConnect.play_replay(r.get("id", 0))
                is_playing_replay = True
                break

        # Flag to restore pre-replay graphic settings after this live session
        AppSettings.replay_playing = True
        AppSettings.save()

        if not is_playing_replay:
            RfactorStatusEvent.set(f"Could not find Replay: {self.data}")
            self.reset_queue = True
            return False

        logging.debug("Playing replay: %s", self.data)
        RfactorLiveEvent.set(True)
        RfactorStatusEvent.set(f"Loading Replay {self.data}")

        self.finished = True
        return True

    def nav_action_method(self):
        if not isinstance(self.data, str):
            logging.error(f"Navigation command needs a string argument")
            return

        # -- Log navigation target
        nav_message = self.data[4:]
        if nav_message.startswith("TO_"):
            nav_message = nav_message[3:]
        RfactorStatusEvent.set(f"Navigating to {nav_message}")
        logging.debug(f"Executing nav action [{nav_message}] command: {self.data}")

        RfactorConnect.post_request(f"/navigation/action/{self.data}")
        self.finished = True

    @staticmethod
    def trigger_app_save_method():
        logging.debug("Executing command App-Settings save.")
        AppSettings.save()

    def get_content_method(self):
        # -- Not supported in LMU for now
        self.finished = True
        return

    def set_content_method(self):
        # -- Not supported in LMU for now
        self.finished = True
        return

    def set_session_settings_method(self):
        if not self.data or not isinstance(self.data, dict):
            logging.error("Command set_session_settings was not provided with data of the correct type!")
            return

        # -- Check API enabled
        if not RfactorConnect.rest_api_enabled:
            logging.info("Skipping command set_session_settings because rF2 REST API use not enabled.")
            self.finished = True
            return

        # -- Update Session Settings
        r = RfactorConnect.get_request("/rest/sessions")
        if not self._check_request(r):
            logging.error("Command set session settings could not get current session settings.")
            return
        current_settings = r.json()

        for key, target_value in self.data.items():
            current_value = current_settings.get(key, dict()).get("currentValue")

            if current_value is None:
                logging.error("Could not locate and update setting: %s in current rF2 session settings", key)
                continue

            if current_value == target_value:
                logging.info("Skipping session setting %s that already has desired value %s", key, target_value)
                continue

            high = int(max(target_value, current_value))
            low = int(min(target_value, current_value))
            direction = 1 if (target_value - current_value) > 0 else 0
            num_sends = high - low

            while (num_sends := num_sends - 1) >= 0:
                retries, result = 3, None
                while (retries := retries - 1) >= 0:
                    logging.debug("Updating setting %s in direction %s", key, direction)
                    s = RfactorConnect.post_request(
                        "/rest/sessions/settings", json={"sessionSetting": key, "value": direction}
                    )
                    if self._check_request(s):
                        result = s.json()
                        break
                    else:
                        logging.info("Re-trying failed set session settings request #%s", retries)
                        gevent.sleep(0.1)

                if result and str(result.get("currentValue")) == str(target_value):
                    break

        AppAudioFx.play_audio(AppAudioFx.switch)
        # -- Navigate to Main Menu
        RfactorConnect.post_request("/navigation/action/NAV_TO_MAIN_MENU", data=None)
        self.finished = True

    def start_race_method(self):
        logging.debug("Executing command start race")
        RfactorStatusEvent.set("Starting Race Session")
        r = RfactorConnect.post_request("/rest/race/startRace")

        AppAudioFx.play_audio(AppAudioFx.confirm)

        if not self._check_request(r):
            return
        self.finished = True

    def drive_method(self):
        logging.debug("Executing command drive")
        RfactorStatusEvent.set("Requesting to Drive")
        r = RfactorConnect.post_request("/rest/garage/drive")

        AppAudioFx.play_audio(AppAudioFx.switch)

        if not self._check_request(r):
            return
        self.finished = True

    def press_key_method(self):
        if self.data:
            RfactorStatusEvent.set(f"Sending key: {self.data}")
            logging.debug("Executing command press key: %s", self.data)
            PressReleaseKey(self.data)
            AppAudioFx.play_audio(AppAudioFx.switch)
        else:
            logging.error("Command press key did not contain any Key Code.")
        self.finished = True

    def press_shift_key_method(self):
        if self.data:
            RfactorStatusEvent.set(f"Sending key + left Shift: {self.data}")
            logging.debug("Executing command press key + LSHIFT: %s", self.data)
            PressKey("DIK_LSHIFT")
            PressReleaseKey(self.data)
            ReleaseKey("DIK_LSHIFT")
        else:
            logging.error("Command press key + LSHIFT did not contain any Key Code.")
        self.finished = True

    def press_ctrl_key_method(self):
        if self.data:
            RfactorStatusEvent.set(f"Sending key + left Ctrl: {self.data}")
            logging.debug("Executing command press key + DIK_LCONTROL: %s", self.data)
            PressKey("DIK_LCONTROL")
            PressReleaseKey(self.data)
            ReleaseKey("DIK_LCONTROL")
        else:
            logging.error("Command press key + DIK_LCONTROL did not contain any Key Code.")
        self.finished = True

    def press_alt_key_method(self):
        if self.data:
            RfactorStatusEvent.set(f"Sending key + left Alt: {self.data}")
            logging.debug("Executing command press key + DIK_LMENU: %s", self.data)
            PressKey("DIK_LMENU")
            PressReleaseKey(self.data)
            ReleaseKey("DIK_LMENU")
        else:
            logging.error("Command press key + DIK_LMENU did not contain any Key Code.")
        self.finished = True

    def timeout_command_method(self):
        start = time.time()
        t = self.data
        if isinstance(t, (int, float)):
            RfactorStatusEvent.set(f"Waiting for {self.data}s")
            gevent.sleep(t)
        logging.debug(f"Executed command timeout for {(time.time() - start):.2f}s")
        self.finished = True

    def record_benchmark_method(self):
        RecordBenchmarkEvent.set(True)
        RfactorStatusEvent.set(f"Recording Benchmark.")
        AppAudioFx.play_audio(AppAudioFx.ping)
        self.finished = True

    def replay_playback_method(self):
        if self.data:
            RfactorConnect.replay_playback_command(self.data)
        else:
            logging.error("Command replay playback did not contain any argument.")
        self.finished = True

    def replay_time_method(self):
        if self.data:
            RfactorConnect.replay_time_command(self.data)
        else:
            logging.error("Command replay time did not contain any time argument.")
        self.finished = True

    def replay_focus_method(self):
        response = RfactorConnect.get_request("/rest/watch/standings")
        if not response:
            self.finished = True
            return

        if response.status_code not in (200, 201, 202, 203, 204):
            self.finished = True
            return

        slot_id = -1
        for standings_entry in response.json():
            if standings_entry.get("driverName") == self.data:
                slot_id = standings_entry.get("slotID", -1)
                break

        if slot_id == -1:
            self.finished = True
            return

        RfactorConnect.put_request(f"/rest/watch/focus/{slot_id}")
        self.finished = True

    def ai_take_control_method(self):
        RfactorStatusEvent.set(f"Requesting AI Control for current vehicle.")
        logging.debug("Requesting AI Control for current vehicle.")
        RfactorConnect.post_request("/rest/sessions/ai/TakeDriverControl")
        self.finished = True

    def to_race_menu_method(self):
        RfactorStatusEvent.set("Returning to race menu")
        logging.debug("Executing command to return race menu")
        RfactorConnect.post_request("/rest/garage/toRaceMenu")
        self.finished = True


class CommandQueue:
    """Queue commands to send to rF2"""

    queue: List[Command] = list()
    current_command: Optional[Command] = None

    # Seconds after last executed command to switch into idle timeouts
    idle_timeout = 30.0
    last_command_time = 0.0

    @classmethod
    def append(cls, command: Command):
        cls.queue.append(command)

    @classmethod
    def reset(cls):
        logging.debug("Resetting rF2 Web Ui Command Queue")
        cls.queue = list()

    @classmethod
    def is_empty(cls):
        return len(cls.queue) == 0

    @classmethod
    def _get_next(cls) -> Optional[Command]:
        cls.current_command = None

        if not cls.is_empty():
            cmd = cls.queue.pop(0)
            cmd.activate()
            cls.current_command = cmd
            return cmd

    @classmethod
    def next(cls) -> Optional[Command]:
        if cls.current_command:
            # -- Check if we should reset the queue
            if cls.current_command.reset_queue:
                cls.reset()
                return cls._get_next()

            # -- Check current Command for timeout
            if cls.current_command.timed_out:
                return cls._get_next()

            # -- Move to next command in queue if the current command was finished
            if cls.current_command.finished:
                return cls._get_next()
            else:
                return cls.current_command

        return cls._get_next()

    @classmethod
    def run(cls):
        # ---------------------------
        # -- COMMAND QUEUE
        # ---------------------------
        command = cls.next()

        if not command and (time.time() - cls.last_command_time) > cls.idle_timeout:
            # -- Reset rF2 FrontEnd status message
            if not RfactorStatusEvent.empty:
                RfactorStatusEvent.set("")
            RfactorConnect.set_to_idle_timeout()

            # -- Call the check connection method every loop
            #    - it will only actually check in it's own time intervals
            #    - will not track loading state if shared memory available
            RfactorConnect.check_connection()
            return

        # -- We have active commands, alter Connection checks accordingly
        # -- Track State changes more frequently
        RfactorConnect.set_to_active_timeout()
        # -- Require to track loading state when checking connection
        RfactorConnect.check_connection()

        # -- Execute command
        if command:
            command.execute()
            cls.last_command_time = time.time()
