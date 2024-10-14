import shutil
from pathlib import Path

import pytest

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
