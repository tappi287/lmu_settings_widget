import logging
import os
import sys
import tomllib
from pathlib import Path
from typing import Union

from appdirs import user_data_dir, user_log_dir

APP_NAME = "lmu_settings_widget"
SETTINGS_DIR_NAME = "lmu_settings_widget"
EXPORT_DIR_NAME = "exported"
PRESETS_DIR = "presets"
DEFAULT_PRESETS_DIR = "default_presets"
DEFAULT_PRESET_NAME = "gfx_Defaults.json"
DATA_DIR = "data"
CHAT_PLUGIN_NAME = "ChatTransceiver.dll"
APP_FRIENDLY_NAME = "LMU Settings Widget"
BASE_PATH = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__ + "/../..")))
RFACTOR_PLAYER = "UserData/player/Settings.JSON"
RFACTOR_CONTROLLER = "UserData/player/direct input.json"
RFACTOR_KEYBOARD = "UserData/player/keyboard.json"
RFACTOR_DXCONFIG = "UserData/Config_DX11.ini"
RFACTOR_DXVRCONFIG = "UserData/Config_DX11_VR.ini"
RFACTOR_VERSION_TXT = "Core/Version.txt"
RFACTOR_SETUPS = "UserData/player/Settings"
RFACTOR_LOG = "UserData/Log"
RFACTOR_PLUGIN_PATH = "Plugins"
RFACTOR_MODMGR = "ModMgr.exe"

GIT_RELEASE_URL = "https://api.github.com/repos/tappi287/rf2_video_settings/releases/latest"

UPDATE_VERSION_FILE = "version.txt"
UPDATE_INSTALL_FILE = "LMU_Settings_Wizard_{version}_win64"

DEFAULT_LOG_LEVEL = "DEBUG"

KNOWN_APPS = {
    "365960": {"name": "rFactor 2", "installdir": "rFactor 2", "executable": "rFactor2.exe", "exe_sub_path": "Bin64/"},
    "908520": {"name": "fpsVR", "installdir": "fpsVR", "executable": "fpsVR.exe", "exe_sub_path": ""},
    "2399420": {
        "name": "Le Mans Ultimate",
        "installdir": "Le Mans Ultimate",
        "executable": "Le Mans Ultimate.exe",
        "exe_sub_path": "",
    },
    "crew_chief": {
        "name": "CrewChief v4",
        "installdir": "",
        "executable": "CrewChiefV4.exe",
        "exe_sub_path": "",
        "simmon_method": "find_by_registry_keys",
        "simmon_method_args": [
            [
                "SOFTWARE\\WOW6432Node\\Britton IT Ltd\\InstalledProducts\\CrewChiefV4",
                "SOFTWARE\\Britton IT Ltd\\InstalledProducts\\CrewChiefV4",
            ],
            "InstallLocation",
        ],
    },
    "kneeboard": {
        "name": "OpenKneeboard",
        "installdir": "",
        "executable": "OpenKneeboardApp.exe",
        "exe_sub_path": "",
        "simmon_method": "find_by_registry_keys_current_user",
        "simmon_method_args": [["SOFTWARE\\Fred Emmott\\OpenKneeboard"], "InstallationBinPath"],
    },
    "sim_hub": {
        "name": "SimHub",
        "installdir": "",
        "executable": "SimHubWPF.exe",
        "exe_sub_path": "",
        "simmon_method": "find_by_registry_keys_current_user",
        "simmon_method_args": [["SOFTWARE\\SimHub"], "InstallDirectory"],
    },
    "pimax_play": {
        "name": "Pimax Play",
        "installdir": "",
        "executable": "PimaxClient.exe",
        "exe_sub_path": "PimaxClient/pimaxui",
        "simmon_method": "find_by_registry_keys",
        "simmon_method_args": [["SOFTWARE\\Pimax"], "InstallPath"],
    },
}

GAME_EXECUTABLE = KNOWN_APPS["2399420"]["executable"]

RF2_APPID = [k for k in KNOWN_APPS.keys()][0]
FPSVR_APPID = [k for k in KNOWN_APPS.keys()][1]
LMU_APPID = [k for k in KNOWN_APPS.keys()][2]

# Frozen or Debugger
if getattr(sys, "frozen", False):
    # -- Running in PyInstaller Bundle ---
    FROZEN = True
else:
    # -- Running in IDE ---
    FROZEN = False

SETTINGS_FILE_NAME = "settings.json" if FROZEN else "settings_dev.json"
SETTINGS_CONTENT_FILE_NAME = "content.json"


def check_and_create_dir(directory: Union[str, Path]) -> str:
    if not os.path.exists(directory):
        try:
            os.mkdir(directory)
            logging.info("Created: %s", directory)
        except Exception as e:
            logging.error("Error creating directory %s", e)
            return ""

    return directory


def get_current_modules_dir() -> str:
    """Return path to this app modules directory"""
    return BASE_PATH


def get_settings_dir() -> Path:
    return Path(check_and_create_dir(user_data_dir(SETTINGS_DIR_NAME, "")))


def get_presets_dir() -> Path:
    settings_dir = get_settings_dir()
    return Path(check_and_create_dir(settings_dir / PRESETS_DIR))


def get_present_mon_bin() -> Path:
    bin_dir = Path(get_current_modules_dir()) / "bin"
    present_mon_exe = bin_dir / "PresentMon-1.9.2-x64.exe"

    for f in bin_dir.glob("PresentMon*.exe"):
        if f:
            present_mon_exe = f
            break

    return present_mon_exe


def get_present_mon_service_loader() -> Path:
    bin_dir = Path(get_current_modules_dir()) / "bin"
    present_mon_service_loader = bin_dir / "PresentMonAPI2Loader.dll"
    return present_mon_service_loader


def _get_user_doc_dir() -> Path:
    docs_dir = Path.home() / "Documents"
    if not docs_dir or not docs_dir.exists():
        docs_dir = os.path.expanduser("~\\Documents\\")
    return Path(docs_dir)


def get_data_dir() -> Path:
    return Path(get_current_modules_dir()) / DATA_DIR


def get_default_presets_dir() -> Path:
    return get_data_dir() / DEFAULT_PRESETS_DIR


def get_log_dir() -> str:
    log_dir = user_log_dir(SETTINGS_DIR_NAME, "")
    setting_dir = os.path.abspath(os.path.join(log_dir, "../"))
    # Create <app-name>
    check_and_create_dir(setting_dir)
    # Create <app-name>/log
    return check_and_create_dir(log_dir)


def get_log_file() -> Path:
    if FROZEN:
        return Path(get_log_dir()) / f"{APP_NAME}.log"
    else:
        return Path(get_log_dir()) / f"{APP_NAME}_DEV.log"


def get_fpsvr_dir() -> Path:
    docs_dir = _get_user_doc_dir()
    if not docs_dir:
        docs_dir = os.path.expanduser("~\\Documents\\")
    return Path(check_and_create_dir(Path(docs_dir) / "fpsVR" / "CSV"))


def get_version() -> str:
    p = Path(get_current_modules_dir()) / "pyproject.toml"
    try:
        with open(p, "rb") as f:
            pyproj = tomllib.load(f)
            return pyproj.get("project", {}).get("version", "0.0.0")
    except Exception as e:
        logging.error(f"Error reading Version: {e}")

    return "0.0.0"


def find_subclasses(module, clazz):
    for name in dir(module):
        o = getattr(module, name)
        try:
            if (o != clazz) and issubclass(o, clazz):
                yield name, o
        except TypeError:
            pass
