from pathlib import Path

from lmu.app_settings import AppSettings
from lmu.lmu_game import RfactorPlayer
from lmu.preset.preset import GraphicsPreset, BasePreset, ControlsSettingsPreset
from lmu.preset.preset_base import PRESET_TYPES, load_presets_from_dir
from lmu.preset.presets_dir import get_user_presets_dir
from lmu.log import setup_logging

setup_logging()


def read_current_presets(preset_type, current_preset) -> tuple[list[BasePreset], BasePreset | None]:
    selected_preset_name = AppSettings.selected_presets.get(str(preset_type)) or current_preset.name

    return load_presets_from_dir(get_user_presets_dir(), preset_type, current_preset, selected_preset_name)


def _break_install_dir(files: list[Path]):
    for file in files:
        file.unlink(missing_ok=True)


def test_read_current_gfx_preset_no_ini(set_test_install_location):
    settings = AppSettings()
    current_preset = PRESET_TYPES.get(GraphicsPreset.preset_type)()

    rf = RfactorPlayer()
    _break_install_dir([rf.ini_file, rf.ini_vr_file])

    if rf.is_valid:
        current_preset.update(rf)

    presets, selected_preset = read_current_presets(GraphicsPreset.preset_type, current_preset)

    # - Check if the currently selected preset differs
    #   from the actual rFactor 2 settings on disk.
    #   If they deviate, point the user to the current settings.
    preset_changed = None
    if selected_preset and selected_preset != current_preset:
        preset_changed = selected_preset.name

    assert rf.write_settings(current_preset) is True


def test_read_current_gfx_preset_no_settings_json(set_test_install_location):
    rf = RfactorPlayer()

    _break_install_dir([rf.player_file])
    current_preset = PRESET_TYPES.get(GraphicsPreset.preset_type)()

    if rf.is_valid:
        current_preset.update(rf)

    assert rf.write_settings(current_preset) is False


def test_read_current_controller_preset_no_controller_json(set_test_install_location):
    rf = RfactorPlayer()

    _break_install_dir([rf.controller_file])
    current_preset = PRESET_TYPES.get(ControlsSettingsPreset.preset_type)()

    if rf.is_valid:
        current_preset.update(rf)

    assert rf.write_settings(current_preset) is False
