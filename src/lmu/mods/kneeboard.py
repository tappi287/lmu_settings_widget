import logging
import subprocess
from pathlib import WindowsPath
from typing import Optional

import psutil

try:
    import winreg as registry

    WINREG_AVAIL = True
except ImportError:
    registry = None
    WINREG_AVAIL = False

from lmu import utils


OPEN_KNEEBOARD_EXECUTABLE = "OpenKneeboardApp.exe"


def open_kneeboard_running() -> bool:
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"].lower().startswith(OPEN_KNEEBOARD_EXECUTABLE.lower()):
            return True
    return False


def get_open_kneeboard_location() -> Optional[WindowsPath]:
    base_key = registry.HKEY_CURRENT_USER
    try:
        key = registry.OpenKey(base_key, "SOFTWARE\\Fred Emmott\\OpenKneeboard")
        values = utils.get_registry_values_as_dict(key)
        bin_dir: str = values.get("InstallationBinPath", dict()).get("data", str())
        if bin_dir:
            open_kneeboard_location = WindowsPath(bin_dir).joinpath("OpenKneeboardApp.exe")
            if open_kneeboard_location.exists():
                return open_kneeboard_location
    except OSError:
        logging.info("OpenKneeboard registry key not found")
    return None


def start_open_kneeboard():
    if open_kneeboard_running():
        logging.debug("OpenKneeboard is already running")
        return

    open_kneeboard_location = get_open_kneeboard_location()
    process = subprocess.Popen(
        open_kneeboard_location, cwd=open_kneeboard_location.parent, creationflags=subprocess.DETACHED_PROCESS
    )
    logging.info(f"OpenKneeBoard process started with PID: {process.pid}")
