import json

from lmu.mods import ext_applications


def _modify_to_not_find_pimax_play():
    # Modify Registry Arg to not find Pixmax Play even if it is present on the test machine
    from lmu.globals import KNOWN_APPS

    KNOWN_APPS["pimax_play"]["simmon_method_args"] = [["SOFTWARE\\PimaxErr"], "InstallPath"]

    # Pre populate SteamApps
    from lmu.lmu_location import STEAM_APPS

    STEAM_APPS.read_steam_library()


def test_get_pimax_play():
    _modify_to_not_find_pimax_play()
    location = ext_applications.get_app_executable_path("pimax_play")
    assert location is None


def test_app_get_pimax_play():
    _modify_to_not_find_pimax_play()
    from lmu.app.app_launch_fn import get_pimax_play_location

    result = get_pimax_play_location()
    result = json.loads(result)
    assert result is not None
    assert result["result"] is False
    assert isinstance(result["msg"], str) is True
