import logging
import re
from datetime import datetime
from pathlib import Path

from lmu.lmu_game import RfactorPlayer
from lmu.utils import create_file_safe_name

REPLAY_FILE_SUFFIX = ".Vcr"


def get_replay_location_from_rfactor_player(rf: RfactorPlayer) -> Path | None:
    if hasattr(rf.options, "game_options"):
        value = rf.options.game_options.get_option("Custom Replay Folder").value
        if value:
            return Path(value)


def get_replays_location() -> Path | None:
    rf = RfactorPlayer()
    if not rf.is_valid:
        return

    return get_replay_location_from_rfactor_player(rf)


def rename_replay(replay: dict, new_name: str, replay_location: Path | None = None):
    try:
        p: Path = replay_location or get_replays_location()
        replay_file: Path = p / f"{replay.get('name', '')}{REPLAY_FILE_SUFFIX}"
        target_file = replay_file.with_stem(create_file_safe_name(new_name, allow_spaces=True))
        replay_file.rename(target_file)
        logging.info("Renaming replay: %s to %s", replay.get("name"), target_file.as_posix())
        return True
    except Exception as e:
        logging.error("Error renaming replay: %s", e)

    return False


def delete_replays(replays: list, replay_location: Path | None = None):
    errors = list()
    p: Path = replay_location or get_replays_location()

    for r in replays:
        try:
            replay_file: Path = p / f"{r.get('name', '')}{REPLAY_FILE_SUFFIX}"
            if replay_file.exists():
                logging.debug("Deleting replay: %s", replay_file.as_posix())
                replay_file.unlink()
        except Exception as e:
            logging.error("Error deleting replay: %s", e)
            errors.append(f"Error deleting replay: {e}")

    if errors:
        return False, errors
    return True, list()


def get_replays(replay_location: Path | None = None) -> list[dict]:
    """Return attributes of all replays as JSON ready list sorted by date"""
    p = replay_location or get_replays_location()
    replays = list()

    for idx, r in enumerate(p.glob(f"*{REPLAY_FILE_SUFFIX}")):
        s = r.stat()

        # Determine type by name
        replay_type = 0
        if re.match(r".*(HOT\sLAP)", r.stem):
            replay_type = 4  # Hot Lap
        elif re.match(r".*(Q\d)\s.*", r.stem):
            replay_type = 1  # Qualy
        elif re.match(r".*(P\d)\s.*", r.stem):
            replay_type = 2  # Practice
        elif re.match(r".*(R\d)\s.*", r.stem):
            replay_type = 3  # Race
        elif re.match(r".*(WU\s\d)", r.stem):
            replay_type = 5  # WarmUp

        replay = {
            "id": idx,
            "name": r.stem,
            "size": f"{s.st_size / 1048576:.2f}MB",
            "ctime": s.st_mtime,
            "type": replay_type,
            "date": datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d %H:%M"),
        }
        replays.append(replay)

    return sorted(replays, key=lambda e: e["ctime"], reverse=True)
