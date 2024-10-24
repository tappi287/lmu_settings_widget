from lmu.rf2replays import get_replays_location


def test_get_replay_folder(set_test_install_location):
    path = get_replays_location()
    print(path)
