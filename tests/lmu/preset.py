from lmu.app_settings import AppSettings
from lmu.lmu_game import RfactorPlayer
from lmu.preset.preset import GraphicsPreset, BasePreset
from lmu.preset.preset_base import PRESET_TYPES, load_presets_from_dir
from lmu.preset.presets_dir import get_user_presets_dir


def read_current_presets(preset_type, current_preset) -> tuple[list[BasePreset], BasePreset | None]:
    selected_preset_name = AppSettings.selected_presets.get(str(preset_type)) or current_preset.name

    return load_presets_from_dir(get_user_presets_dir(), preset_type, current_preset, selected_preset_name)


def test_read_current_gfx_preset(set_test_install_location):
    settings = AppSettings()
    current_preset = PRESET_TYPES.get(GraphicsPreset.preset_type)()

    rf = RfactorPlayer()
    if rf.is_valid:
        current_preset.update(rf)

    presets, selected_preset = read_current_presets(GraphicsPreset.preset_type, current_preset)

    # - Check if the currently selected preset differs
    #   from the actual rFactor 2 settings on disk.
    #   If they deviate, point the user to the current settings.
    if selected_preset and selected_preset != current_preset:
        preset_changed = selected_preset.name
