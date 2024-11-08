""" Functionality to handle installation of the ReShade Open XR API Layer """

import logging
from pathlib import Path

from lmu.globals import get_data_dir
from lmu.utils import get_registry_values_as_dict

try:
    from pathlib import WindowsPath
    import winreg as registry

    WINREG_AVAIL = True
except ImportError:
    registry, WindowsPath = None, Path
    WINREG_AVAIL = False

RESHADE_OPENXR_LAYER_DIR = "reshade_openxr_layer"
RESHADE_OPENXR_LAYER_JSON = "ReShade64_XR.json"
RESHADE_OPENXR_APPS_INI = "ReShadeApps.ini"
OPEN_XR_API_LAYER_REG_PATH = "SOFTWARE\\Khronos\\OpenXR\\1\\ApiLayers\\Implicit"


def reshade_openxr_layer_dir() -> Path:
    return get_data_dir() / RESHADE_OPENXR_LAYER_DIR


def reshade_openxr_json_path() -> str:
    return str(WindowsPath(reshade_openxr_layer_dir() / RESHADE_OPENXR_LAYER_JSON))


def reshade_openxr_apps_ini_path() -> str:
    return str(WindowsPath(reshade_openxr_layer_dir() / RESHADE_OPENXR_APPS_INI))


def update_reshade_openxr_apps_ini(game_executable: Path) -> bool:
    reshade_apps_ini_path = Path(reshade_openxr_apps_ini_path())
    if not reshade_apps_ini_path.exists():
        logging.error(f"Could not locate ReShade OpenXR Apps INI file: {reshade_apps_ini_path}")
        return False

    utf8_bom = b"\xef\xbb\xbf"
    game_executable_win_path = str(WindowsPath(game_executable))

    with open(reshade_apps_ini_path, "rb") as f:
        data = f.read()

    if data.startswith(utf8_bom):
        text = data[3:].decode("utf-8")
    else:
        text = data.decode("utf-8")

    paths_text, paths = text[5:], list()  # remove Apps=
    if paths_text:
        # Read existing paths
        paths = paths_text.replace("\n", "").replace("\r", "").split(",")
        paths = [p for p in paths if p != ""]

    # Path already in INI
    if game_executable_win_path in paths:
        return True

    # Add path
    paths.append(game_executable_win_path)

    # Write to file
    eof = "\r\n" * 3
    out_text = f"Apps={','.join(paths)}{eof}"

    with open(reshade_apps_ini_path, "wb") as f:
        out_bytes = utf8_bom
        out_bytes += out_text.encode("utf-8")
        f.write(out_bytes)

    return True


def is_openxr_layer_installed() -> int:
    """Check if the ReShade OpenXR API Layer is set up.

    :returns: 0 - if not installed, 1 - installed and active, -1 - installed but deactivated
    """
    if not WINREG_AVAIL:
        logging.error(f"Windows registry not available, can not check OpenXR-API-Layer installation")
        return 0

    # -- Open OpenXR v1 API Layers registry key
    try:
        key = registry.OpenKey(registry.HKEY_CURRENT_USER, OPEN_XR_API_LAYER_REG_PATH)
        values = get_registry_values_as_dict(key)
        if reshade_openxr_json_path() in values:
            value = values.get(reshade_openxr_json_path())
            if value.get("data") == 0:
                return 1
            else:
                return -1
    except OSError as e:
        logging.error(f"Could not open or create registry key: {e}")
        return 0


def remove_reshade_openxr_layer() -> bool:
    if not WINREG_AVAIL:
        logging.error(f"Windows registry not available, skipping OpenXR-API-Layer setup")
        return False

    # -- Open OpenXR v1 API Layers registry key
    layer_present = False
    try:
        key = registry.OpenKey(registry.HKEY_CURRENT_USER, OPEN_XR_API_LAYER_REG_PATH, access=registry.KEY_ALL_ACCESS)
        if reshade_openxr_json_path() in get_registry_values_as_dict(key):
            layer_present = True
    except OSError as e:
        logging.error(f"Could not read registry key: {e}")
        return False

    if layer_present:
        registry.DeleteValue(key, reshade_openxr_json_path())
    return True


def setup_reshade_openxr_layer(enable=True, game_executable: Path = None) -> bool:
    """Setup ReShade via it's OpenXR-API-Layer
        this will end up in HKEY_CURRENT_USER\SOFTWARE\Khronos\OpenXR\1\ApiLayers\Implicit

        https://registry.khronos.org/OpenXR/specs/1.0/loader.html#windows-manifest-registry-usage

    :return:
    """
    if not WINREG_AVAIL:
        logging.error(f"Windows registry not available, skipping OpenXR-API-Layer setup")
        return False

    # -- Update ReShade Apps INI
    if game_executable is not None:
        update_reshade_openxr_apps_ini(game_executable)

    # -- Open or create OpenXR v1 API Layers registry key
    try:
        key = registry.CreateKey(registry.HKEY_CURRENT_USER, OPEN_XR_API_LAYER_REG_PATH)
    except OSError as e:
        logging.error(f"Could not open or create registry key: {e}")
        return False

    # -- Get the path to reshade openxr dir which is equal to the name of the value
    reshade_path_value = reshade_openxr_json_path()

    # -- Get existing values
    existing_values = get_registry_values_as_dict(key)

    # Layer already setup
    if reshade_path_value in existing_values:
        reshade_layer_enabled = existing_values[reshade_path_value]["data"] == 0
        if reshade_layer_enabled and enable:
            logging.debug(
                f"Reshade OpenXR API Layer already enabled: " f"{existing_values[reshade_path_value]['data']}"
            )
            return True

    # -- Set DWORD value to 0 to enable the layer or non-zero to disable the layer
    try:
        registry.SetValueEx(key, reshade_path_value, 0, registry.REG_DWORD, 0 if enable else 1)
    except OSError as e:
        logging.error(f"Could not set ReShade OpenXR API Layer value: {e}")
        return False

    return True
