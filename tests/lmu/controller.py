import pygame

from lmu.lmu_game import RfactorPlayer
from lmu.preset.preset import PresetType
from lmu.preset.preset_base import PRESET_TYPES
from lmu.utils import create_js_joystick_device_list, map_lmu_device_to_pygame_device


def test_controls_preset(set_test_install_location, app_settings_test_dir):
    app_settings = app_settings_test_dir
    current_preset = PRESET_TYPES.get(PresetType.controls)()

    rf = RfactorPlayer()
    current_preset.update(rf)

    pygame.joystick.init()
    py_game_device_list = create_js_joystick_device_list(app_settings.controller_devices)
    lmu_device_map = map_lmu_device_to_pygame_device(
        py_game_device_list,
        rf.controller_devices
    )
    print(lmu_device_map)

    # Assign a device not in JSON
    current_preset.general_controller_assignments.options[2].value = {"device": "Non-ExistingDevice", "id": 24}
    rf.write_settings(current_preset)

