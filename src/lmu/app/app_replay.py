import eel

import lmu.app
from . import app_replay_fn


def expose_replay_methods():
    pass


@eel.expose
def get_replays():
    return app_replay_fn.get_replays()


@eel.expose
def get_replay_preset():
    return app_replay_fn.get_replay_preset()


@eel.expose
def set_replay_preset(preset_name):
    return app_replay_fn.set_replay_preset(preset_name)


@eel.expose
def delete_replays(replays: list):
    return app_replay_fn.delete_replays(replays)


@eel.expose
def rename_replay(replay: dict, new_name: str):
    return app_replay_fn.rename_replay(replay, new_name)


@eel.expose
def focus_driver(driver_name: str):
    return app_replay_fn.focus_driver(driver_name)


@eel.expose
def play_replay(replay_name):
    return lmu.app.app_replay_fn.play_replay(replay_name)


@eel.expose
def replay_playback_command(playback_command: int | str):
    return lmu.app.app_replay_fn.replay_playback_command(playback_command)


@eel.expose
def replay_time_command(replay_time: float | str):
    return lmu.app.app_replay_fn.replay_time_command(replay_time)
