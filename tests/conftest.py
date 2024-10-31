import os
import shutil
from pathlib import Path

import pytest

from lmu.app_settings import AppSettings
from lmu.globals import SETTINGS_FILE_NAME

test_data_input_path = Path(__file__).parent.joinpath("data/input")
test_data_output_path = Path(__file__).parent.joinpath("data/output")
test_data_output_path.mkdir(exist_ok=True)
LMU = "Le Mans Ultimate"


@pytest.fixture
def lmu_test_install_dir() -> Path:
    shutil.copytree(test_data_input_path.joinpath(LMU), test_data_output_path.joinpath(LMU))
    return test_data_output_path / LMU


@pytest.fixture
def clean_test_install_dir() -> None:
    lmu_test_install_path = test_data_output_path.joinpath(LMU)
    if lmu_test_install_path.exists():
        shutil.rmtree(lmu_test_install_path)


@pytest.fixture
def test_data_output_dir() -> Path:
    return test_data_output_path


@pytest.fixture
def set_test_install_location(clean_test_install_dir, lmu_test_install_dir) -> Path:
    from lmu.lmu_location import RfactorLocation

    RfactorLocation.set_location(lmu_test_install_dir)
    return lmu_test_install_dir


@pytest.fixture
def set_install_and_replay_result_files(clean_test_install_dir, lmu_test_install_dir, test_data_output_dir):
    from lmu import rf2replays
    from lmu.lmu_location import RfactorLocation

    RfactorLocation.set_location(lmu_test_install_dir)

    replay_mtimes = list()
    for p in rf2replays.get_replays_location().glob(f"*{rf2replays.REPLAY_FILE_SUFFIX}"):
        replay_mtimes.append(p.stat().st_mtime)

    for p in test_data_output_dir.joinpath("Le Mans Ultimate/UserData/Log/Results").glob("*.*"):
        if not p.is_file():
            continue
        if not replay_mtimes:
            break
        new_mtime = replay_mtimes.pop()
        os.utime(p, (p.stat().st_ctime, new_mtime))


def _overwrite_settings_dir():
    return test_data_output_path / SETTINGS_FILE_NAME


@pytest.fixture
def app_settings_test_dir() -> type(AppSettings):
    AppSettings._get_settings_file = _overwrite_settings_dir
    return AppSettings
