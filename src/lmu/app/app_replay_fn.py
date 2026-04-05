import json
import logging
from typing import Optional

import eel

from .. import rf2replays
from ..app_settings import AppSettings
from ..lmu_game import RfactorPlayer
from ..preset.preset import GraphicsPreset, PresetType
from ..preset.preset_base import load_presets_from_dir, PRESET_TYPES
from ..preset.presets_dir import get_user_presets_dir
from ..preset.settings_model import VideoSettings, GameOptions
from ..rf2command import CommandQueue, Command
from ..rf2connect import RfactorState, RfactorConnect
from ..rf2events import RfactorLiveEvent
from ..utils import capture_app_exceptions


@capture_app_exceptions
def get_replays():
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({"result": False, "msg": rf.error})

    # Sort by change date
    return json.dumps({"result": True, "replays": rf2replays.get_replays(rf)})


@capture_app_exceptions
def get_replay_preset():
    logging.debug("Providing replay preset name: %s", AppSettings.replay_preset)
    return AppSettings.replay_preset


@capture_app_exceptions
def set_replay_preset(preset_name):
    AppSettings.replay_preset = preset_name
    logging.debug("Updated replay preset name to: %s", AppSettings.replay_preset)
    AppSettings.save()


@capture_app_exceptions
def delete_replays(replays: list):
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({"result": False, "msg": rf.error})

    result, errors = rf2replays.delete_replays(replays, rf2replays.get_replay_location_from_rfactor_player(rf))

    if errors:
        return json.dumps({"result": False, "msg": "; ".join(errors)})

    return json.dumps({"result": True})


@capture_app_exceptions
def rename_replay(replay: dict, new_name: str):
    if not new_name:
        return json.dumps({"result": False, "msg": "Enter a name containing at least one character."})

    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({"result": False, "msg": rf.error})

    if rf2replays.rename_replay(replay, new_name, rf2replays.get_replay_location_from_rfactor_player(rf)):
        return json.dumps({"result": True})

    return json.dumps({"result": False, "msg": f"Error renaming replay."})


@capture_app_exceptions
def focus_driver(driver_name: str):
    if not driver_name:
        return json.dumps({"result": False, "msg": f"No driver name provided."})
    CommandQueue.append(Command(Command.replay_focus, data=driver_name, timeout=10.0))
    return json.dumps({"result": True, "msg": f"Switching to driver {driver_name}"})


def apply_gfx_preset_with_name(rf: RfactorPlayer, preset_name: str) -> Optional[GraphicsPreset]:
    _, selected_preset = load_presets_from_dir(
        get_user_presets_dir(), PresetType.graphics, selected_preset_name=preset_name
    )
    if selected_preset:
        rf.write_settings(selected_preset)
        eel.sleep(0.01)
        return selected_preset


def apply_disable_play_movies(rf: RfactorPlayer):
    # -- Apply Play Movies 0
    current_adv_preset = PRESET_TYPES.get(PresetType.advanced_settings)()
    current_adv_preset.update(rf)
    advanced_settings: GameOptions = getattr(
        current_adv_preset, GameOptions.app_key, GameOptions()
    )
    play_movies_opt = advanced_settings.get_option("Play Movies")
    play_movies_opt.value = 0
    rf.write_settings(current_adv_preset)
    eel.sleep(0.01)


def _switch_replay_while_live(replay_name):
    # 1. Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.api_available, timeout=120.0))
    # 2. Back to main menu
    CommandQueue.append(Command(Command.nav_action, data="NAV_BACK_TO_MAIN_MENU", timeout=20.0))
    # 3. Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=20.0))
    # 4. Load Replay
    CommandQueue.append(Command(Command.play_replay, replay_name, timeout=30.0))
    return json.dumps({"result": True, "msg": f"Switching to replay: {replay_name}"})


@capture_app_exceptions
def play_replay(replay_name):
    if not replay_name:
        return json.dumps({"result": False, "msg": "No Replay name provided."})

    # -- Switch replay while live
    is_live = RfactorLiveEvent.get_nowait()
    if is_live:
        return _switch_replay_while_live(replay_name)

    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps({"result": False, "msg": rf.error})

    # -- Apply replay graphics preset
    replay_gfx_preset = apply_gfx_preset_with_name(rf, AppSettings.replay_preset)
    video_settings: VideoSettings = getattr(replay_gfx_preset, VideoSettings.app_key, VideoSettings())
    launch_option = video_settings.get_option("Launch")
    launch_method = 1
    if launch_option:
        launch_method = launch_option.value

    # -- Apply Play Movies: 0
    #    applies the current Gfx Preset with Play Movies set to 0
    #    has no effect in v1.3
    # apply_disable_play_movies(rf)

    # -- Start rFactor 2
    result = rf.run_rfactor(method=launch_method)
    if result and rf.pid >= 0:
        RfactorConnect.rf2_pid = rf.pid

    if not result:
        # -- Restore non-replay graphics preset
        selected_preset_name = AppSettings.selected_presets.get(str(PresetType.graphics))
        if selected_preset_name:
            apply_gfx_preset_with_name(rf, selected_preset_name)
            logging.info("Restored non-replay preset %s", selected_preset_name)
        return json.dumps({"result": False, "msg": f"Could not launch LMU: {rf.error}"})

    # -- Tell the rFactor Greenlet to play a replay in next iteration
    # 1. Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.api_available, timeout=120.0))
    # 2. Skip intro video
    CommandQueue.append(Command(Command.timeout_command, data=12.0, timeout=15.0))
    CommandQueue.append(Command(Command.press_key, data="DIK_SPACE", timeout=2.0))
    CommandQueue.append(Command(Command.press_key, data="DIK_SPACE", timeout=2.0))
    CommandQueue.append(Command(Command.press_key, data="DIK_SPACE", timeout=2.0))
    CommandQueue.append(Command(Command.timeout_command, data=1.0, timeout=5.0))
    # 2. Load Replay
    CommandQueue.append(Command(Command.play_replay, replay_name, timeout=15.0))
    # 3. Wait UI Loading State
    # CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.loading, timeout=60.0))
    # 4. Wait UI Ready State
    # CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.api_available, timeout=800.0))
    # 5. Switch FullScreen
    # CommandQueue.append(Command(Command.nav_action, data="NAV_TO_FULL_EVENT_MONITOR", timeout=30.0))

    return json.dumps({"result": True, "msg": rf.error})


@capture_app_exceptions
def replay_playback_command(playback_command: int | str):
    playback_command = int(playback_command)
    CommandQueue.append(Command(Command.replay_playback, playback_command, timeout=5.0))
    return json.dumps({"result": True})


@capture_app_exceptions
def replay_time_command(replay_time: float | str):
    replay_time = float(replay_time)
    CommandQueue.append(Command(Command.replay_time, replay_time, timeout=5.0))
    return json.dumps({"result": True})
