import json
import os
import shutil
import winreg
from pathlib import Path
from subprocess import Popen
from typing import Union

from lmu import eel_mod
from lmu.globals import UPDATE_INSTALL_FILE, UPDATE_VERSION_FILE, get_version, get_current_modules_dir
from scripts.patch_sdl_pygame import patch_sdl_lib_pygame

os.chdir(get_current_modules_dir())

VERSION = get_version()

SPEC_FILE = "app.spec"
ISS_FILE = "lmu_settings_widget_win64_setup.iss"
ISS_VER_LINE = "#define MyAppVersion"
ISS_SETUP_EXE_FILE = UPDATE_INSTALL_FILE.format(version=VERSION)
PORTABLE_ZIP_NAME = f"{UPDATE_INSTALL_FILE.format(version=VERSION)}_portable"

VUE_DIR = "vue/package.json"
BUILD_DIR = "build"
DIST_DIR = "dist"
DIST_EXE_DIR = "LMU-Settings-Widget"


class FindInnoSetup:
    inno_console_compiler_name = "ISCC.exe"

    @staticmethod
    def _open_registry():
        return winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    @classmethod
    def _get_by_inno_studio_compiler_option(cls, reg) -> Union[None, Path]:
        """Find the key set by Inno Studio when compiler path set in options"""
        try:
            key = winreg.OpenKey(reg, r"SOFTWARE\Classes\InnoSetupScriptFile\shell\Compile\command", 0, winreg.KEY_READ)
        except OSError:
            return

        value = winreg.EnumValue(key, 0)[1]  # "C:\\Program Files (x86)\\Inno Setup 6\\Compil32.exe" /cc "%1"
        value = value[0 : value.find("/cc") - 1]  # "C:\\Program Files (x86)\\Inno Setup 6\\Compil32.exe"
        return Path(value.replace('"', "")).parent

    @classmethod
    def _get_by_inno_setup_uninstall_key(cls, reg) -> Union[None, Path]:
        """Find by either Inno Setup 5 or 6 Uninstall Key"""
        keys = [
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 5_is1",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1",
        ]
        key = None

        while keys:
            try:
                key = winreg.OpenKey(reg, keys.pop(), 0, winreg.KEY_READ)
            except OSError:
                pass

        if key is None:
            return

        idx, name, value = 0, str(), str()
        while 1:
            try:
                name, value, __ = winreg.EnumValue(key, idx)
            except OSError:
                # Will break when no more sub key values are available
                return

            idx += 1
            if name == "InstallLocation" and value:
                break

        return Path(value.replace('"', ""))

    @classmethod
    def compiler_path(cls) -> Union[None, Path]:
        methods = [cls._get_by_inno_setup_uninstall_key, cls._get_by_inno_studio_compiler_option]
        reg = cls._open_registry()

        value = None
        while methods:
            m = methods.pop()
            value = m(reg)

            if value is not None:
                break

        if value is None:
            return

        return value / cls.inno_console_compiler_name  # eg. 'C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe'


def update_version_info(out_dir: Path):
    # Write version file
    print("Creating/Updating version info file.\n")
    file = out_dir / UPDATE_VERSION_FILE
    with open(file.as_posix(), "w") as f:
        f.write(VERSION)

    with open(ISS_FILE, "r") as f:
        iss_lines = f.readlines()

    print("Updating Inno Setup Script")
    for idx, line in enumerate(iss_lines):
        if line.startswith(ISS_VER_LINE):
            line = f'{ISS_VER_LINE} "{VERSION}"\n'
            iss_lines[idx] = line
            print("updated: " + iss_lines[idx] + "\n")

    with open(ISS_FILE, "w") as f:
        f.writelines(iss_lines)

    with open(Path(get_current_modules_dir()).joinpath(VUE_DIR), "r") as f:
        package_json = json.load(f)
        package_json["version"] = VERSION
    with open(Path(get_current_modules_dir()).joinpath(VUE_DIR), "w") as f:
        json.dump(package_json, f, indent=4)
        print("Updated package.json version", VERSION)
    # Update exe manifest
    # update_manifest_version()


def remove_dist_info_dirs():
    dist_dir = Path(DIST_DIR) / Path(DIST_EXE_DIR)
    for d in dist_dir.glob("*.dist-info"):
        if not d.is_dir():
            continue
        shutil.rmtree(d)


def run_npm_build():
    # -- Run npm and build web package
    cd = Path(".") / "vue"
    cmd = ["npm", "run", "build-lmu"]

    p = Popen(args=cmd, shell=True, cwd=cd.as_posix())
    p.wait()


def copy_eel_cache_file():
    web_dir = Path("web")
    if web_dir.exists():
        shutil.copy(eel_mod.eel_cache_js_file(), web_dir / "assets")


def run_pyinstaller(spec_file: str):
    args = ["pyinstaller", "--noconfirm", spec_file]
    p = Popen(args=args)
    result = p.communicate()
    print("Pyinstaller result: " + str(p.returncode), result)

    return p.returncode


def create_portable_archive():
    archive_file = Path(DIST_DIR) / PORTABLE_ZIP_NAME
    dist_exe_dir = Path(DIST_DIR) / DIST_EXE_DIR
    portable_dist_dir = Path(DIST_DIR) / "portable" / PORTABLE_ZIP_NAME
    archive_root_dir = Path(DIST_DIR) / "portable"

    portable_dist_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(dist_exe_dir, portable_dist_dir, dirs_exist_ok=True)

    old_archive = Path(DIST_DIR) / f"{PORTABLE_ZIP_NAME}.zip"
    old_archive.unlink(missing_ok=True)

    print("Creating portable archive:", archive_file.as_posix())
    shutil.make_archive(archive_file.as_posix(), format="zip", root_dir=archive_root_dir)

    shutil.rmtree(archive_root_dir, ignore_errors=True)


def main(process: int = 0):
    if process == -1:
        print("Aborting process.")
        return

    print("\n### STARTING LMU Settings Widget BUILD ###")

    # Remove build dir
    print("Removing build dir to avoid building with outdated web dir.")
    build_dir = Path(BUILD_DIR)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    build_dir.mkdir()

    update_version_info(build_dir)

    if process in (0, 1, 2):
        run_npm_build()
        copy_eel_cache_file()
        patch_sdl_lib_pygame()

        # Build with PyInstaller
        result = run_pyinstaller(SPEC_FILE)

        if result != 0:
            print("PyInstaller could not build executable!")
            return

        # Copy/Add external applications
        dist_dir = Path(DIST_DIR) / Path(DIST_EXE_DIR)

        remove_dist_info_dirs()

    if process in (1, 2):
        iss_path = FindInnoSetup.compiler_path()
        if iss_path is None or not iss_path.exists():
            print("Could not find Inno Setup compiler path.")
            return

        args = [FindInnoSetup.compiler_path().as_posix(), ISS_FILE]
        print("\nRunning Inno Setup console-mode compiler...\n", args)
        p = Popen(args, cwd=get_current_modules_dir())
        p.wait()

        print("Inno Setup console-mode compiler result: " + str(p.returncode))

        if p.returncode != 0:
            print("Inno Script Studio encountered an error!")
            return

    if process in (1, 2):
        # -- Create Portable Archive
        create_portable_archive()

        rm_dir = Path(DIST_DIR) / Path(DIST_EXE_DIR)
        if rm_dir.exists():
            print("Removing executable folder:", rm_dir)
            shutil.rmtree(rm_dir)

        print("\nBuild completed!")


def ask_process() -> int:
    print("\n\n" "##########################################################")
    print(
        "Choose which process you'd like to proceed with:\n"
        "\t\t0 - Build Executable\n"
        "\t\t1 - Build Executable + Installer\n"
    )

    answer = input("Answer: ")

    if answer not in ["0", "1", "q", "exit", "quit"]:
        ask_process()

    if answer.isdigit():
        return int(answer)
    else:
        return -1


if __name__ == "__main__":
    process_option = ask_process()

    main(process_option)
