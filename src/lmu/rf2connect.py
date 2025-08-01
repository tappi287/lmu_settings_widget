import logging
import time
from queue import Queue, Empty
from threading import Event, Thread
from typing import Optional, Union

import gevent
import psutil

from lmu import requests
from lmu.directInputKeySend import PressReleaseKey
from lmu.globals import GAME_EXECUTABLE
from lmu.rf2sharedmem.sharedMemoryAPI import SimInfoAPI
from lmu.lmu_game import RfactorPlayer
from lmu.utils import rfactor_process_with_id_exists

CONNECTION_DEBUG = False


class RfactorState:
    unavailable = 0
    loading = 1
    ready = 2
    waiting_for_process = 10

    names = {0: "Unavailable", 1: "Loading", 2: "Ready"}


class _RfactorConnectRequestThread:
    # -- Threaded requests
    request_queue = Queue()
    response_queue = Queue()
    close_event = Event()
    request_thread: Optional[Thread] = None

    @staticmethod
    def _request_thread_loop(request_queue: Queue, response_queue: Queue, close_event: Event):
        logging.debug("RfactorConnect request thread started.")

        while not close_event.is_set():
            # -- Check for requests
            try:
                r = request_queue.get(timeout=1.0)
            except Empty:
                continue

            # -- Fulfill request
            if r.get("method") == "GET":
                try:
                    response = RfactorConnect.get_request(r.get("url"))
                except WindowsError:
                    continue
                except Exception as e:
                    logging.error("Error during GET request: %s", e)
                    continue

                response_json = False
                if response:
                    if response.status_code in (200, 201, 202, 203, 204):
                        response_json = response.json()
                    else:
                        logging.debug(
                            "Request Thread received error response for GET request to %s %s %s",
                            r.get("url"),
                            response.status_code,
                            response.text,
                        )
                        response_json = {"status_code": response.status_code}

                response_queue.put(response_json)
            elif r.get("method") == "POST":
                try:
                    response = RfactorConnect.post_request(r.get("url"), r.get("data"))
                except Exception as e:
                    logging.error("Error during POST request: %s", e)
                    continue

                if response.status_code not in (200, 201, 202, 203, 204):
                    logging.debug(
                        "Request Thread received error response for POST request to %s %s %s",
                        r.get("url"),
                        response.status_code,
                        response.text,
                    )
                response_queue.put(response or False)  # Make sure we do not put None in the queue

        logging.debug("RfactorConnect request thread exiting.")

    @classmethod
    def check_response(cls) -> Optional[dict]:
        response = None
        # Make sure to collect all responses
        while cls.response_queue.qsize() > 0:
            try:
                response = cls.response_queue.get_nowait()
            except Empty:
                break
        return response

    @classmethod
    def start_request_thread(cls):
        cls.request_thread = Thread(
            target=cls._request_thread_loop, args=(cls.request_queue, cls.response_queue, cls.close_event)
        )
        cls.request_thread.start()

    @classmethod
    def stop_request_thread(cls) -> None:
        logging.debug("Stopping RfactorConnect request thread.")
        cls.close_event.set()
        if cls.request_thread.is_alive():
            logging.debug("Joining RfactorConnect request thread.")
            cls.request_thread.join(timeout=5.0)
            logging.debug("RfactorConnect request thread joined.")


class RfactorConnect:
    """Helper class to connect to a running rF2 instance WebUi and request current rF2 state and call
    WebUi endpoints to control the running instance.
    """

    host = "localhost"
    web_ui_port: int = 0  # Call update_web_ui_port to update the port from current player.json
    state = 0  # RfactorState
    get_request_time = 0.5  # float seconds timeout for get requests

    long_timeout = 120.0  # Maximum connection check timeout
    idle_timeout = 15.0  # Start with this time out after an active connection
    active_timeout = 1.0  # Check connection timeout while eg. loading

    last_connection_check = time.time()
    connection_check_interval = idle_timeout  # Revalidate connection every float seconds

    # -- Track rF2 available state changes
    last_rfactor_live_state = False

    # -- Shared memory
    shared_memory_obj = SimInfoAPI()
    enable_shared_mem_check = None
    rf2_pid = None

    # -- Performance monitoring
    present_mon = None

    _timestamp = 0

    @staticmethod
    def start_request_thread():
        _RfactorConnectRequestThread.start_request_thread()

    @staticmethod
    def stop_request_thread() -> None:
        _RfactorConnectRequestThread.stop_request_thread()

    @classmethod
    def base_url(cls) -> str:
        return f"http://{cls.host}:{cls.web_ui_port}"

    @classmethod
    def get_pid(cls) -> int:
        for proc in psutil.process_iter(["pid", "name"]):
            if proc.info["name"].lower().startswith(GAME_EXECUTABLE.lower()):
                cls.rf2_pid = proc.info["pid"]
                logging.info("Found Game Executable Process ID: %s", cls.rf2_pid)
                return cls.rf2_pid
        logging.info("Could not find Game Executable with Process ID: %s", cls.rf2_pid)
        return -1

    @classmethod
    def _rf2_processes_detected(cls) -> bool:
        if rfactor_process_with_id_exists(cls.rf2_pid):
            return True

        if cls.get_pid() >= 0:
            return True
        return False

    @classmethod
    def _shared_memory_check(cls):
        # -- Check if shared Memory available
        if not cls.shared_memory_obj.sharedMemoryVerified:
            if cls.shared_memory_obj.isRF2running():
                if not cls.shared_memory_obj.isSharedMemoryAvailable():
                    logging.info("Shared memory not available: Disabling Shared Memory Updates")
                    cls.enable_shared_mem_check = False
                    return
        # -- Shared Memory available
        else:
            if not cls.shared_memory_obj.isRF2running():
                # -- Do an extra check for running rF2 processes
                if cls._rf2_processes_detected():
                    cls.set_to_active_timeout()
                    # -- Shared memory no longer available but UI processes still running
                    return

                # -- Set unavailable
                logging.info("Setting rF2 State to unavailable from shared memory state.")
                cls.state = RfactorState.unavailable
                cls.check_for_rf_pid = True

    @classmethod
    def check_connection(cls) -> None:
        """Check if Web UI connection is available every timeout interval
        or use shared memory if reported to be available.
        """
        response = _RfactorConnectRequestThread.check_response()
        if response is not None:
            cls.set_state(response)
            return

        if cls.enable_shared_mem_check:
            cls._shared_memory_check()

        # - Only check every connection_check_interval
        timeout = min(cls.long_timeout, cls.connection_check_interval)
        if time.time() - cls.last_connection_check < timeout:
            return

        # -- Increase timeout with every check
        if cls.connection_check_interval < cls.long_timeout:
            cls.connection_check_interval = cls.connection_check_interval * 1.1

        # -- Find WebUI port if not already known
        if cls.web_ui_port == 0:
            if not cls.update_web_ui_port():
                return

        # -- Check navigation state in http request thread
        if _RfactorConnectRequestThread.request_queue.empty():
            # logging.debug('Checking for rFactor 2 http connection. Interval: %.2f', timeout)
            cls.last_connection_check = time.time()  # Update TimeOut
            _RfactorConnectRequestThread.request_queue.put({"method": "GET", "url": "/navigation/state"})

    @classmethod
    def set_state(cls, nav_state: Union[bool, dict]) -> None:
        previous_state = int(cls.state)

        if isinstance(nav_state, dict):
            if nav_state.get("status_code", 200) != 200:
                # -- Assume loading state if we received a request with a non 200 status
                cls.state = RfactorState.loading
            else:
                # -- Set State loading or ready
                cls.state = (
                    RfactorState.loading
                    if nav_state.get("loadingStatus", dict()).get("loading")
                    else RfactorState.ready
                )
        elif nav_state is False:
            if cls._rf2_processes_detected():
                # -- UI Processes still active
                #    wait for them to shut down
                cls.state = RfactorState.waiting_for_process
                cls.set_to_active_timeout()
                return
            # -- Set unavailable
            cls.state = RfactorState.unavailable
            cls.enable_shared_mem_check = None

        if previous_state != cls.state:
            if cls.state in (RfactorState.loading, RfactorState.waiting_for_process):
                cls.set_to_active_timeout()
            elif cls.state == RfactorState.unavailable:
                cls.set_to_idle_timeout()
            elif cls.state == RfactorState.ready and cls.enable_shared_mem_check is None:
                logging.info("Enabling Shared Memory Updates")
                cls.enable_shared_mem_check = True
            logging.debug("Updating rFactor 2 state to: %s", RfactorState.names.get(cls.state))

    @classmethod
    def get_replays(cls) -> list:
        """Request all replays from the rFactor 2 UI"""
        cls.wait_for_rf2_ui(5.0)
        if cls.state != RfactorState.ready:
            return list()

        r = cls.get_request("/rest/watch/replays")
        if r is None:
            logging.debug("Could not get Replay list from rFactor 2 WebUi.")
            return list()
        if r.status_code not in (200, 204):
            logging.debug("Could not get Replay list from rFactor 2 WebUi.")
            return list()

        return r.json()

    @classmethod
    def play_replay(cls, replay_id: int) -> bool:
        """Request rFactor 2 to play the replay with the provided id"""
        cls.wait_for_rf2_ui(5.0)
        if cls.state != RfactorState.ready:
            return False

        r = cls.get_request(f"/rest/watch/play/{replay_id}")
        if r.status_code not in (200, 204):
            logging.debug(f"Request to play Replay #{replay_id} failed.")
            return False
        return True

    @classmethod
    def replay_playback_command(cls, command: int) -> bool:
        """0 - Jump to Start   |<
        1 - Jump to End     >|
        2-5 - Super Fast Reverse, Fast Reverse, Play Reverse, Slow-Mo Reverse
        6 - Pause
        7-10 - Slow-Mo Forward, Play Forward, Fast Forward, Super Fast Forward
        """
        if cls.state != RfactorState.ready:
            return False
        r = cls.put_request("/rest/watch/replayCommand", json=command)
        if r.status_code not in (200, 204):
            logging.debug(f"Request to Replay ReplayCommand #{command} failed.")
            return False
        return True

    @classmethod
    def replay_time_command(cls, replay_time: float):
        """/rest/replay/replaytime PUT"""
        if cls.state != RfactorState.ready:
            return False
        r = cls.put_request("/rest/replay/replaytime", json=replay_time)
        if r.status_code not in (200, 204):
            logging.debug(f"Request to Replay Time {replay_time} failed.")
            return False
        return True

    @classmethod
    def quit(cls) -> bool:
        """Requests rFactor 2 to quit"""
        PressReleaseKey("DIK_ESCAPE")  # Hit Escape

        cls.wait_for_rf2_ui(5.0)
        if cls.state != RfactorState.ready:
            return False

        r = cls.post_request("/navigation/action/NAV_EXIT")

        return True if r and r.status_code in (200, 201, 202, 203, 204) else False

    @classmethod
    def set_to_active_timeout(cls):
        """Track state changes more frequently"""
        if cls.connection_check_interval > cls.active_timeout:
            cls.connection_check_interval = cls.active_timeout

    @classmethod
    def set_to_idle_timeout(cls):
        """Track state changes in idle"""
        if cls.connection_check_interval < cls.idle_timeout:
            cls.connection_check_interval = cls.idle_timeout

    @classmethod
    def wait_for_rf2_ui(cls, timeout_secs: float, wait_for_state_change: bool = False):
        """Wait for a rFactor 2 Web UI connection in ready state"""
        start_time = time.time()
        previous_state = int(cls.state)
        cls.set_to_active_timeout()

        while not time.time() - start_time > timeout_secs:
            cls.check_connection()
            if wait_for_state_change and cls.state != previous_state:
                wait_for_state_change = False
            if cls.state == RfactorState.ready and not wait_for_state_change:
                return
            gevent.sleep(0.5)

        logging.info("Waiting for active rF Web UI timed out.")

    @classmethod
    def get_request(cls, url) -> Optional[requests.RequestResponse]:
        try:
            r = requests.get(f"{cls.base_url()}{url}", timeout=cls.get_request_time)
        except Exception as e:
            if CONNECTION_DEBUG:
                logging.debug("Error during get request: %s", e)
            return

        if r.status_code not in (200, 201, 202, 203, 204):
            logging.info("Request failed to %s, status %s, data %s", url, r.status_code, r.text)

        return r

    @classmethod
    def post_request(cls, url, data=None, json=None, headers=None) -> Optional[requests.RequestResponse]:
        try:
            r = requests.post(f"{cls.base_url()}{url}", data=data, json=json, headers=headers)
        except Exception as exc:
            logging.error("Could not connect to rFactor 2 Web UI: %s", exc)
            return

        logging.info("Response for POST request to %s was %s %s", url, r.status_code, r.text)
        return r

    @classmethod
    def put_request(cls, url, data=None, json=None, headers=None) -> Optional[requests.RequestResponse]:
        try:
            r = requests.put(f"{cls.base_url()}{url}", data=data, json=json, headers=headers)
        except Exception as exc:
            logging.error("Could not connect to rFactor 2 Web UI: %s", exc)
            return

        logging.info("Response for PUT request to %s was %s %s", url, r.status_code, r.text)
        return r

    @staticmethod
    def update_web_ui_port() -> bool:
        rf = RfactorPlayer()
        if rf.is_valid:
            if hasattr(rf.options, "misc_options"):
                o = rf.options.misc_options.get_option("WebUI port")
                RfactorConnect.web_ui_port = o.value
                logging.debug("Updated RfactorConnect Web UI port to: %s", RfactorConnect.web_ui_port)
                return True
        return False
