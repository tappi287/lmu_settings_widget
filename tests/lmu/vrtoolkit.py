from lmu.lmu_game import RfactorPlayer
from lmu.mods.vrtoolkit import VrToolKit
from lmu.preset.settings_model import OptionsTarget


def test_vr_tool_kit_validate_extra_files(set_test_install_location):
    ply = RfactorPlayer()
    vr_tool_kit = VrToolKit(ply._get_target_options(OptionsTarget.reshade), ply.location)

    assert vr_tool_kit.validate_extra_files(install_missing=False) is False
    assert vr_tool_kit.validate_extra_files(install_missing=True) is True
