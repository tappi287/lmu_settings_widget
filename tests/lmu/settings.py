from pathlib import Path

from lmu.globals import SETTINGS_FILE_NAME
from lmu.lmu_location import RfactorLocation
from lmu.app_settings import AppSettings
from lmu.log import setup_logging

setup_logging(__name__)
TEST_OUT_DIR = Path(".")


def _overwrite_settings_dir():
    return TEST_OUT_DIR / SETTINGS_FILE_NAME


def test_app_settings_load(clean_test_install_dir, lmu_test_install_dir, test_data_output_dir):
    RfactorLocation.set_location(lmu_test_install_dir)

    settings = AppSettings()
    assert settings.first_load_complete is False
    settings.load()
    assert settings.first_load_complete is True
    print(settings)


def test_app_settings_save(clean_test_install_dir, lmu_test_install_dir, test_data_output_dir):
    global TEST_OUT_DIR
    TEST_OUT_DIR = test_data_output_dir
    AppSettings._get_settings_file = _overwrite_settings_dir