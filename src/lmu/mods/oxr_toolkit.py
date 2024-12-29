import logging
from pathlib import Path

from lmu.utils import get_registry_values_as_dict

try:
    import winreg as registry

    WINREG_AVAIL = True
except ImportError:
    registry = None
    WINREG_AVAIL = False


OXR_TOOLKIT_KEY = "Software\\OpenXR_Toolkit"
LMU_SETTINGS_KEY = "OpenComposite_Le Mans Ultimate"


def get_oxr_toolkit_settings_registry_values(base_key=None) -> dict:
    if not WINREG_AVAIL:
        return dict()

    if base_key is None:
        base_key = registry.HKEY_CURRENT_USER

    sub_key = Path(OXR_TOOLKIT_KEY) / LMU_SETTINGS_KEY
    try:
        key = registry.OpenKey(base_key, sub_key.as_posix().replace("/", "\\"))
        return get_registry_values_as_dict(key)
    except OSError as e:
        logging.error(f"Could not open registry key: {e}")

    return dict()
