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

    # Assign a device not in JSON
    current_preset.general_controller_assignments.options[2].value = {"device": "Non-ExistingDevice", "id": 24}
    rf.write_settings(current_preset)

    controller_json_dict = rf.read_player_json_dict(rf.controller_file, encoding='cp1252')
    for input_, assignment in controller_json_dict["Input"].items():
        if not assignment:
            continue
        assert assignment["device"] in controller_json_dict["Devices"]


def test_lmu_device_map(app_settings_test_dir):
    rf = RfactorPlayer()
    controller_json_dict = rf.read_player_json_dict(rf.controller_file, encoding='cp1252')
    rf.read_controller_devices(controller_json_dict)

    pygame.joystick.init()
    py_game_device_list = create_js_joystick_device_list(app_settings_test_dir.controller_devices)
    # Add fake test device if none connected
    if not py_game_device_list:
        py_game_device_list.append({"guid": "0123-Test-Id", "name": "Test-Device"})
        rf.controller_devices.update({
            "Test-Device:ArbitaryInfo-01234ID": {"product name": "Test-Device"}
        })

    lmu_device_map = map_lmu_device_to_pygame_device(
        py_game_device_list,
        rf.controller_devices
    )

    for device in py_game_device_list:
        assert device["guid"] in lmu_device_map
        assert lmu_device_map[device["guid"]] in rf.controller_devices
