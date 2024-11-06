import logging
import winreg as registry
from pathlib import Path, WindowsPath

from lmu.globals import GAME_EXECUTABLE
from lmu.mods import vrtoolkit
from lmu.utils import get_registry_values_as_dict


def test_reshade_registry_setup():
    vrtoolkit.VrToolKit.setup_reshade_openxr()

    key = registry.OpenKey(registry.HKEY_CURRENT_USER, vrtoolkit.VrToolKit.OPEN_XR_API_LAYER_REG_PATH)
    values = get_registry_values_as_dict(key)

    reshade_path_value = vrtoolkit.VrToolKit.reshade_openxr_json_path()
    assert reshade_path_value in values


def test_update_reshade_openxr_apps_ini(set_test_install_location):
    update_reshade_openxr_apps_ini(set_test_install_location / GAME_EXECUTABLE)
