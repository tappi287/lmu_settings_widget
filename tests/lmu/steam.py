import subprocess

from lmu.lmu_location import RfactorLocation
from lmu.valve.steam_utils import SteamApps


def test_find_steam_linux():
    p = subprocess.run(["bash", "-c", "command", "-v", "steam"], check=True, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(p.stdout)


def test_find_steam_game():
    s = SteamApps()
    s.read_steam_library()
    path = s.find_game_location(RfactorLocation._app_id)
    print(path)