import json
import logging
import subprocess
from pathlib import WindowsPath, Path
from typing import Optional

from lmu.app_settings import AppSettings
from lmu.lmu_game import RfactorPlayer
from lmu.rf2command import CommandQueue, Command
from lmu.rf2connect import RfactorState
from lmu.utils import capture_app_exceptions
from lmu.mods import ext_applications
from lmu.valve.steam_utils import SteamApps


@capture_app_exceptions
def get_last_launch_method() -> Optional[int]:
    return AppSettings.last_launch_method


@capture_app_exceptions
def run_rfactor(server_info: Optional[dict] = None, method: Optional[int] = 0):
    logging.info("UI requested rF2 run with method: %s", method)
    if method is None:
        method = AppSettings.last_launch_method
        logging.info("Launching rF2 with last known method: %s", method)

    if server_info and server_info.get("password_remember"):
        # -- Store password if remember option checked
        logging.info("Storing password for Server %s", server_info.get("id"))
        AppSettings.server_passwords[server_info.get("id")] = server_info.get("password")
        AppSettings.save()
    elif server_info and not server_info.get("password_remember"):
        # -- Delete password if remember option unchecked
        if server_info.get("id") in AppSettings.server_passwords:
            AppSettings.server_passwords.pop(server_info.get("id"))
            AppSettings.save()

    AppSettings.last_launch_method = method
    AppSettings.save()

    # -- Autostart external applications
    for app_key in AppSettings.app_preferences.get("autostart"):
        try:
            ext_applications.start_application(app_key)
        except Exception as e:
            logging.error(f"Error calling autostart function: {app_key}: {e}")

    # -- Run game
    rf, result = RfactorPlayer(), False
    if rf.is_valid:
        result = rf.run_rfactor(method, server_info)
        if not server_info:
            CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))

    return json.dumps({"result": result, "msg": rf.error})


@capture_app_exceptions
def run_steamvr():
    try:
        steam_path = Path(SteamApps.find_steam_location()) / "steam.exe"
        cmd = [str(WindowsPath(steam_path)), "-applaunch", "250820"]
        subprocess.Popen(cmd)
    except Exception as e:
        return json.dumps({"result": False, "msg": f"Error launching SteamVR: {e}"})
    return json.dumps({"result": True, "msg": "Launched SteamVR"})


@capture_app_exceptions
def get_open_kneeboard_location():
    location = ext_applications.get_app_executable_path("kneeboard")
    if location:
        return json.dumps({"result": True, "data": location.as_posix()})
    return json.dumps({"result": False, "msg": f"Could not get open kneeboard location: {location}"})


@capture_app_exceptions
def get_pimax_play_location():
    location = ext_applications.get_app_executable_path("pimax_play")
    if location:
        return json.dumps({"result": True, "data": location.as_posix()})
    return json.dumps({"result": False, "msg": f"Could not get Pimax Play Client location: {location}"})


@capture_app_exceptions
def launch_pimax_play():
    msg = "Launched Pimax Play"
    try:
        ext_applications.start_application("pimax_play")
        return json.dumps({"result": True, "msg": msg})
    except Exception as e:
        msg = f"Error calling autostart for Pimax Play Client: {e}"
        logging.error(msg)

    return json.dumps({"result": False, "msg": msg})
