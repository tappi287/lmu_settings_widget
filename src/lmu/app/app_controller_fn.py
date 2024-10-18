import json
import logging

from ..app_settings import AppSettings
from ..gamecontroller import ControllerEvents
from ..lmu_game import RfactorPlayer
from ..utils import capture_app_exceptions, create_js_joystick_device_list, map_lmu_device_to_pygame_device


@capture_app_exceptions
def start_controller_capture():
    # Start receiving Controller Events including axis events for input mapping
    ControllerEvents.capturing = True

    logging.debug('Started capturing game controller events for input mapping')


@capture_app_exceptions
def stop_controller_capture():
    ControllerEvents.capturing = False

    logging.debug('Stopped capturing game controller events for input mapping')


@capture_app_exceptions
def get_device_list():
    return json.dumps(create_js_joystick_device_list(AppSettings.controller_devices))


@capture_app_exceptions
def save_device_list(js_device_list):
    for device in js_device_list:
        if device.get('guid') in AppSettings.controller_devices:
            AppSettings.controller_devices[device.get('guid')] = device

    AppSettings.save()


@capture_app_exceptions
def remove_from_device_list(device_guid):
    if device_guid in AppSettings.controller_devices:
        AppSettings.controller_devices.pop(device_guid)
        AppSettings.save()


@capture_app_exceptions
def get_lmu_to_pygame_device_map():
    rf = RfactorPlayer()
    if not rf.is_valid:
        return json.dumps(dict())

    py_game_device_list = create_js_joystick_device_list(AppSettings.controller_devices)
    return json.dumps(
        map_lmu_device_to_pygame_device(
            py_game_device_list,
            rf.controller_devices
        )
    )
