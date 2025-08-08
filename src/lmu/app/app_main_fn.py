import json
import logging
from pathlib import WindowsPath, Path
from subprocess import Popen

from lmu.app_settings import AppSettings
from lmu.globals import DEFAULT_PRESET_NAME, RFACTOR_SETUPS, RFACTOR_MODMGR, get_log_file, get_log_dir, get_data_dir
from lmu.lmu_game import RfactorPlayer
from lmu.lmu_location import RfactorLocation
from lmu.mods import openxr
from lmu.preset.preset import PresetType
from lmu.preset.preset_base import load_preset
from lmu.rf2events import EnableMetricsEvent, EnableRestAPIEvent
from lmu.utils import capture_app_exceptions


def _get_rf_location(sub_path):
    rf = RfactorPlayer(only_version=True)
    rf_path = rf.location / sub_path
    if not rf_path.exists():
        logging.error("Could not locate rF2 Setups directory in %s", rf_path.as_posix())
        return
    return str(WindowsPath(rf_path))


@capture_app_exceptions
def overwrite_rf_location(value):
    def reset_location():
        AppSettings.rf_overwrite_location = ""
        RfactorLocation.overwrite_location(None)

    if Path(value).exists() and Path(value).is_dir() and Path(value) != Path(""):
        AppSettings.rf_overwrite_location = Path(value).as_posix()
        RfactorLocation.overwrite_location(AppSettings.rf_overwrite_location)
        RfactorLocation.get_location()
        if not RfactorLocation.is_valid:
            logging.warning(f"Invalid overwrite location: {value}. Resetting rF2 location.")
            reset_location()
            result = False
        else:
            logging.warning("Overwriting rf2 location: %s", Path(value).as_posix())
            result = True
    else:
        reset_location()
        logging.warning("Overwriting rf2 location cleared!")
        result = True

    AppSettings.save()
    return result


@capture_app_exceptions
def rf_is_valid():
    rf = RfactorPlayer()
    logging.info("Detected valid rF2 installation: %s %s", rf.is_valid, rf.location)
    return json.dumps(rf.is_valid)


@capture_app_exceptions
def restore_backup():
    rf = RfactorPlayer()

    # -- Restore some default settings and remove ReShade etc.
    default_preset_file = get_data_dir() / DEFAULT_PRESET_NAME
    default_preset = load_preset(default_preset_file, PresetType.graphics)
    rf.write_settings(default_preset)

    try:
        openxr.remove_reshade_openxr_layer()
    except Exception as e:
        logging.error(f"Error removing ReShade OpenXR API layer: {e}")

    if not rf.is_valid:
        return json.dumps({"result": False, "msg": rf.error})

    if AppSettings.restore_backup(rf):
        logging.info("Original settings restored!")
        return json.dumps({"result": True, "msg": "BackUp files restored!"})

    return json.dumps(
        {
            "result": False,
            "msg": "Could not restore all back up files! Make sure you " "did not deleted any *.original files!",
        }
    )


@capture_app_exceptions
def get_rf_version():
    rf = RfactorPlayer(only_version=True)
    AppSettings.last_rf_location = rf.location.as_posix()
    AppSettings.save()
    return json.dumps({"version": rf.version, "location": str(rf.location)})


@capture_app_exceptions
def open_setup_folder():
    setup_path = _get_rf_location(RFACTOR_SETUPS)
    if setup_path is None:
        return
    logging.info("Opening folder: %s", setup_path)
    Popen(f'explorer /n,"{setup_path}"')


@capture_app_exceptions
def run_mod_mgr():
    mod_mgr_path = _get_rf_location(RFACTOR_MODMGR)
    if mod_mgr_path is None:
        return
    logging.info("Opening ModMgr: %s", mod_mgr_path)
    Popen(mod_mgr_path, cwd=WindowsPath(mod_mgr_path).parent.parent)


@capture_app_exceptions
def get_log():
    log_file_path = get_log_file()
    try:
        with open(log_file_path, "r") as l:
            return json.dumps({"result": True, "log": l.read()}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"result": False, "msg": str(e)})


@capture_app_exceptions
def open_log_folder():
    log_dir = str(WindowsPath(get_log_dir()))
    logging.info("Opening folder: %s", log_dir)
    Popen(f'explorer /n,"{log_dir}"')
    return json.dumps(
        {
            "result": True,
        }
    )


@capture_app_exceptions
def set_apply_webui_settings(setting: bool):
    AppSettings.apply_webui_settings = setting
    AppSettings.save()
    logging.debug("Updated apply_webui_settings: %s", AppSettings.apply_webui_settings)
    return json.dumps(
        {
            "result": True,
        }
    )


@capture_app_exceptions
def get_apply_webui_settings():
    logging.debug("Providing Ui with apply_webui_settings: %s", AppSettings.apply_webui_settings)
    return json.dumps({"result": True, "setting": AppSettings.apply_webui_settings})


@capture_app_exceptions
def save_app_preferences(app_preferences: dict):
    AppSettings.app_preferences = app_preferences
    AppSettings.update_preferences((EnableMetricsEvent, EnableRestAPIEvent))
    AppSettings.save()
    return json.dumps({"result": True})


@capture_app_exceptions
def load_app_preferences():
    AppSettings.update_preferences((EnableMetricsEvent, EnableRestAPIEvent))
    return json.dumps({"result": True, "preferences": AppSettings.app_preferences})


@capture_app_exceptions
def is_original_openvr_present():
    rf_loc = _get_rf_location("")
    if rf_loc is None:
        return json.dumps({"result": False})

    return json.dumps({"result": openxr.is_openvr_present(Path(rf_loc))})
