from pathlib import Path

from lmu import rf2replays


def test_get_replay_folder(set_test_install_location):
    path = rf2replays.get_replays_location()
    assert path == Path(r"C:\py\lmu_settings_widget\tests\data\input\Le Mans Ultimate\UserData\Replays")


def test_get_replays(set_install_and_replay_result_files):
    replays = rf2replays.get_replays()
    replay_names = [r["name"] for r in replays]

    assert "Autodromo Nazionale Monza P1 1" in replay_names
    assert "Bahrain International Circuit R1 1" in replay_names

    assert replays[0]["type"] == 3 and replays[0]["name"] == "Fuji Speedway R1 1"
    assert replays[1]["type"] == 1 and replays[1]["name"] == "Fuji Speedway Q1 1"
    assert replays[5]["type"] == 2 and replays[5]["name"] == "Autodromo Nazionale Monza P1 1"
