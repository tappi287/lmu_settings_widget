import winreg as registry

from lmu.globals import GAME_EXECUTABLE
from lmu.mods import vrtoolkit, openxr
from lmu.utils import get_registry_values_as_dict
from lmu.log import setup_logging

setup_logging()


def test_reshade_registry_setup():
    openxr.setup_reshade_openxr_layer()

    key = registry.OpenKey(registry.HKEY_CURRENT_USER, vrtoolkit.VrToolKit.OPEN_XR_API_LAYER_REG_PATH)
    values = get_registry_values_as_dict(key)

    reshade_path_value = openxr.reshade_openxr_json_path()
    assert reshade_path_value in values


def test_update_reshade_openxr_apps_ini(set_test_install_location):
    openxr.update_reshade_openxr_apps_ini(set_test_install_location / GAME_EXECUTABLE)


def test_remove_reshade_openxr_layer():
    assert openxr.remove_reshade_openxr_layer() is True
    assert openxr.is_openxr_layer_installed() == 0


def test_deactivate_reshade_openxr_layer():
    openxr.setup_reshade_openxr_layer(enable=False)
    assert openxr.is_openxr_layer_installed() == -1
