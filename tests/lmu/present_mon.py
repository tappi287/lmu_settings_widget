from lmu.lmu_game import RfactorPlayer
from lmu.log import setup_logging

setup_logging()


def test_watch_game_bin():
    ply = RfactorPlayer()
    ply.run_rfactor_with_present_mon(2)
