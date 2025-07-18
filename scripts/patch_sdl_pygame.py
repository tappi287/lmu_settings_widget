import logging
import os
import shutil
from pathlib import Path
import site
from typing import Optional

from lmu.globals import get_current_modules_dir
from lmu.log import setup_logging
from lmu.utils import get_version_string

setup_logging()


def get_lmu_widget_sdl_bin() -> Path:
    bin_dir = Path(get_current_modules_dir()) / "bin"
    return bin_dir / "SDL2.dll"


def get_sdl_version(sdl_bin_path: Path) -> Optional[str]:
    v = get_version_string(sdl_bin_path.as_posix(), "FileVersion")
    return v.replace(", ", ".")


def get_pygame_package_path() -> Optional[Path]:
    pygame_path = None
    for site_path in site.getsitepackages():
        if Path(site_path).joinpath("pygame").exists():
            pygame_path = Path(site_path).joinpath("pygame")
    return pygame_path


def patch_sdl_lib_pygame() -> bool:
    pygame_path = get_pygame_package_path()
    if not pygame_path:
        logging.error(f"Pygame package path not found")
        return False

    pygame_sdl_path = pygame_path / "SDL2.dll"
    if not pygame_sdl_path.exists():
        logging.error(f"PyGame SDL2.dll not found: {pygame_sdl_path}")
        return False
    pygame_sdl_ver = get_sdl_version(pygame_sdl_path)
    logging.info(f"Found PyGame SDL2 v{pygame_sdl_ver} bin at: {pygame_sdl_path}")

    lmu_widget_sdl_path = get_lmu_widget_sdl_bin()
    if not lmu_widget_sdl_path.exists():
        logging.error(f"LMU widget SDL binary not found {lmu_widget_sdl_path}")
        return False
    lmu_widget_sdl_ver = get_sdl_version(lmu_widget_sdl_path)

    if lmu_widget_sdl_ver != pygame_sdl_ver:
        try:
            pygame_sdl_path.replace(pygame_sdl_path.with_suffix(".org"))
            shutil.copyfile(lmu_widget_sdl_path, pygame_sdl_path)
        except Exception as e:
            logging.error(f"Error replacing pygame SDL2 SDL bin: {e}")
            return False

    return True


if __name__ == "__main__":
    patch_sdl_lib_pygame()
