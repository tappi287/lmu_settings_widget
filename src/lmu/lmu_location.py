import logging
from pathlib import Path
from typing import Optional

from lmu.globals import (
    LMU_APPID,
    RFACTOR_PLAYER,
    RFACTOR_CONTROLLER,
    RFACTOR_KEYBOARD,
    RFACTOR_DXCONFIG,
    RFACTOR_DXVRCONFIG,
    RFACTOR_VERSION_TXT,
)
from lmu.valve.steam_utils import SteamApps


class RfactorLocation:
    path: Optional[Path] = None
    player_json = Path()
    controller_json = Path()
    keyboard_json = Path()
    dx_config = Path()
    dx_vr_config = Path()
    version_txt = Path()
    _app_id = LMU_APPID
    is_valid = False

    @classmethod
    def overwrite_location(cls, location):
        # -- Reset Paths
        cls.player_json = Path()
        cls.controller_json = Path()
        cls.keyboard_json = Path()
        cls.dx_config = Path()
        cls.dx_vr_config = Path()
        cls.version_txt = Path()
        cls.is_valid = False

        # -- Update from overwrite
        if location is not None:
            cls.path = Path(location)
        else:
            cls.path = None

    @classmethod
    def set_location(cls, path: Path):
        if not path.exists():
            return

        player_json = path / RFACTOR_PLAYER
        controller_json = path / RFACTOR_CONTROLLER
        keyboard_json = path / RFACTOR_KEYBOARD
        dx_config = path / RFACTOR_DXCONFIG
        dx_vr_config = path / RFACTOR_DXVRCONFIG
        version_txt = path / RFACTOR_VERSION_TXT

        logging.info(
            f"Setting rF location:\n"
            f"{path}\n"
            f"{player_json}\n"
            f"{controller_json}\n"
            f"{dx_config}\n"
            f"{dx_vr_config}\n"
            f"{version_txt}"
        )

        if player_json.exists() and (dx_config.exists() or dx_vr_config.exists()):
            cls.is_valid = True
            cls.path = path
            cls.player_json = player_json
            cls.controller_json = controller_json
            cls.keyboard_json = keyboard_json
            cls.dx_config = dx_config
            cls.dx_vr_config = dx_vr_config
            cls.version_txt = version_txt
        else:
            logging.warning(f"Could not find a valid installation in {path.as_posix()}")

    @classmethod
    def get_location(cls):
        # -- Path maybe already set by overwrite location
        if cls.path is None or not cls.path.exists():
            try:
                s = SteamApps()
                s.read_steam_library()
                path = s.find_game_location(cls._app_id)
            except Exception as e:
                logging.error("Error getting Le Mans Ultimate location from Steam: %s", e)
                return
        else:
            path = cls.path

        if path:
            cls.set_location(path)
