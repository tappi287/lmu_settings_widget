import json
import logging
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path, WindowsPath
from typing import Optional, Iterator, Union, Type

from lmu.globals import LMU_APPID, GAME_EXECUTABLE
from lmu.lmu_location import RfactorLocation
from lmu.preset.preset import BasePreset, PresetType
from lmu.preset.settings_model import BaseOptions, OptionsTarget
from lmu.preset.settings_model_base import OPTION_CLASSES
from lmu.valve.steam_utils import SteamApps
from lmu.mods.vrtoolkit import VrToolKit


class RfactorPlayer:
    resolution_key = "resolution_settings"
    config_parser_args = {
        "inline_comment_prefixes": ("//",),
        "comment_prefixes": ("#", ";", "//"),
        "default_section": "COMPONENTS",
    }
    webui_session_settings = dict()
    webui_content_selection = dict()

    class Options:
        def __init__(self):
            for field, base_cls in OPTION_CLASSES.items():
                options_instance = base_cls()
                setattr(self, field, options_instance)

    def __init__(self, only_version: bool = False, player_json_data: dict = None):
        self.player_json_import_data = player_json_data
        self.player_file = Path()
        self.controller_file = Path()
        self.keyboard_file = Path()
        self.ini_file = Path()
        self.ini_vr_file = Path()
        self.ini_first_line = str()
        self.location = Path("../modules")
        self.version_file = Path()
        self.version = ""

        self.options = self.Options()
        self.controller_devices = dict()

        self.is_valid = False
        self.error = ""

        self.get_current_rfactor_settings(only_version)

    def get_current_rfactor_settings(self, only_version: bool = True):
        """Read all settings from the current Le Mans Ultimate installation"""
        self._get_location()

        if not self._read_version():
            self.error += "Could not read Le Mans Ultimate version\n"
        if only_version:
            return

        if self.player_json_import_data is not None:
            # -- Use player.json data provided on init
            player_json = self.player_json_import_data
        else:
            # -- Read Player JSON
            player_json = self.read_player_json_dict(self.player_file, encoding="utf-8")

        # -- Get Options from Player JSON
        r = self._read_options_from_target(OptionsTarget.player_json, player_json)
        del player_json

        # -- Read Controller JSON
        controller_json = self.read_player_json_dict(self.controller_file, encoding="cp1252")
        self.read_controller_devices(controller_json)
        r = self._read_options_from_target(OptionsTarget.controller_json, controller_json) and r
        del controller_json

        # -- Read Keyboard JSON
        keyboard_json = self.read_player_json_dict(self.keyboard_file, encoding="cp1252")
        self._read_options_from_target(OptionsTarget.keyboard_json, keyboard_json)
        del keyboard_json

        if not r:
            # -- Error reading either player or controller JSON
            return

        # -- Read dx_config
        config = self.read_dx_ini()
        if not config:
            self.is_valid = False
            return
        # -- Get Options from dx_config
        for preset_options in self._get_target_options(OptionsTarget.dx_config):
            if not self._get_options_from_dx_config(preset_options, config):
                self.error += f"Could not read LMU CONFIG_DX11.ini for " f"{preset_options.__class__.__name__}\n"
                self.is_valid = False
                return

        # -- Get ReShade Options
        vr_toolkit = VrToolKit(self._get_target_options(OptionsTarget.reshade), self.location)

        result = vr_toolkit.read()
        if not result:
            self.error += f"{vr_toolkit.error}\n"

        self.is_valid = True

    def _get_target_options(self, target: OptionsTarget, options=None) -> Iterator[BaseOptions]:
        if options is None:
            options = self.options

        for k, v in options.__dict__.items():
            if isinstance(v, BaseOptions):
                if v.target == target:
                    yield v

    def _read_options_from_target(self, target: OptionsTarget, json_dict) -> bool:
        for preset_options in self._get_target_options(target):
            if not self._get_options_from_player_json(preset_options, json_dict) and preset_options.mandatory:
                self.error += f"Could not read LMU settings for " f"{preset_options.__class__.__name__}\n"
                self.is_valid = False
                return False
        return True

    def write_settings(self, preset: BasePreset) -> bool:
        """Writes all settings of a preset into the Le Mans Ultimate installation

        :param preset:
        :return:
        """
        # -- Write video config to dx_config
        self._write_video_config(preset)
        self._write_video_config(preset, True)

        # -- Write reshade settings
        self.write_mod(preset, VrToolKit)

        # -- Update WebUi Session Settings and Content Selection
        self.update_webui_settings(preset, OptionsTarget.webui_session)
        self.update_webui_settings(preset, OptionsTarget.webui_content)

        # -- Update Player Json settings
        player_json_dict = self.read_player_json_dict(self.player_file, encoding="utf-8")
        update_result = self._write_to_target(OptionsTarget.player_json, preset, player_json_dict)

        # -- Update Controller Json settings
        controller_json_dict = self.read_player_json_dict(self.controller_file, encoding="cp1252")
        preset.additional_write_operations(controller_json=controller_json_dict)
        update_result = (
            self._write_to_target(OptionsTarget.controller_json, preset, controller_json_dict) and update_result
        )

        if not update_result:
            return False

        # -- Write JSON files
        r = self.write_json(player_json_dict, self.player_file, encoding="utf-8")
        return r and self.write_json(controller_json_dict, self.controller_file, encoding="cp1252")

    def update_webui_settings(self, preset, target):
        for preset_options in self._get_target_options(target, preset):
            if target == OptionsTarget.webui_session:
                self.webui_session_settings = preset_options.to_webui_js()
            elif target == OptionsTarget.webui_content:
                self.webui_content_selection = preset_options.to_webui_js()

    def write_json(self, json_dict: dict, file: Path, encoding: str = "UTF-8") -> bool:
        try:
            with open(file, "w", encoding=encoding) as f:
                json.dump(json_dict, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.error += f"Error while writing file! {e}\n"
            logging.fatal(self.error)
            return False
        return True

    def _write_to_target(self, target: OptionsTarget, preset: BasePreset, json_dict: dict) -> bool:
        for preset_options in self._get_target_options(target, preset):
            if not self._update_player_json(json_dict, preset_options):
                return False
        return True

    def _write_video_config(self, preset: BasePreset, vr_ini=False):
        """Update the Config_DX11.ini with supported Video Settings"""
        settings_updated = False
        ini_config = self.read_dx_ini(vr_ini)
        if not ini_config:
            logging.error(f"Could not read video settings ini file.")
            return

        ini_file = self.ini_vr_file if vr_ini else self.ini_file

        for preset_options in self._get_target_options(OptionsTarget.dx_config, preset):
            for option in preset_options.options:
                if option.key not in ini_config[ini_config.default_section]:
                    self.error += f"Could not locate settings key: {option.key} in CONFIG_DX11.ini\n"
                    logging.error(self.error)
                    continue
                if option.value is not None:
                    ini_config[ini_config.default_section][option.key] = str(option.value)
                    logging.info("Updated Dx Setting: %s: %s", option.key, option.value)
                    settings_updated = True

        if not settings_updated:
            logging.info("Found no updated Video Settings. Skipping update of dx_config!")
            return

        # -- Write Video Config.ini
        try:
            if ini_file.exists():
                # - Write config
                with open(ini_file, "w") as f:
                    ini_config.write(f, space_around_delimiters=False)

            # - Restore first ini comment line
            with open(ini_file, "r") as f:
                f_lines = f.readlines()
            f_lines = [self.ini_first_line] + f_lines

            # - Remove trailing new line
            if f_lines[-1] == "\n":
                f_lines = f_lines[:-1]
            # - Remove trailing new line character
            f_lines[-1] = f_lines[-1].rstrip("\n")

            # - Write modified config
            with open(ini_file, "w") as f:
                f.writelines(f_lines)
        except Exception as e:
            self.error += f"Could not write CONFIG_DX11.ini file! {e}\n"
            logging.error(self.error)
            return False

    def _update_player_json(self, player_json_dict, preset_options: BaseOptions):
        if not player_json_dict:
            return False

        if preset_options.key not in player_json_dict:
            self.error += f"Could not locate CATEGORY settings key: {preset_options.key} in <Settings>.JSON.\n"
            logging.error(self.error)
            return False

        for option in preset_options.options:
            if option.key in preset_options.skip_keys:
                continue
            if option.key not in player_json_dict[preset_options.key] and not option.create_in_json:
                logging.warning("Skipping Setting: %s in <Settings>.JSON that could not be located!", option.key)
                continue
            if option.value is None:
                logging.debug("Skipping write of %s because value is None.", option.key)
                continue

            player_json_dict[preset_options.key][option.key] = option.value
            logging.info("Updated Setting: %s: %s", option.key, option.value)

            # -- Write duplicate keys e.g. GPRIX RaceTime + CURNT RaceTime
            duplicates_list = option.dupl or list()
            if isinstance(option.dupl, str):
                duplicates_list = [option.dupl]
            for key in duplicates_list:
                player_json_dict[preset_options.key][key] = option.value
                logging.info("Updated duplicated Setting: %s: %s", key, option.value)

        return True

    def write_mod(self, preset: BasePreset, mod_type: Union[Type[VrToolKit]]) -> bool:
        if preset.preset_type != PresetType.graphics or mod_type not in (VrToolKit,):
            return True
        if not self._check_bin_dir():
            self.error += "Could not locate Le Mans Ultimate Bin directory.\n"
            return False

        target = None
        if mod_type is VrToolKit:
            target = OptionsTarget.reshade

        mod = mod_type(self._get_target_options(target, preset), self.location)

        result = mod.write()
        if not result:
            self.error = mod.error

        return result

    @staticmethod
    def _get_options_from_dx_config(video_settings: BaseOptions, config: ConfigParser) -> bool:
        if not config:
            return False
        config_dict = config[config.default_section]

        settings_updated = False
        for option in video_settings.options:
            if option.key not in config_dict:
                option.exists_in_rf = False
                option.hidden = True
                continue
            value = config_dict.get(option.key)
            if option.ini_type is int:
                value = int(value)
            option.value = value
            option.exists_in_rf = True
            settings_updated = True

        return settings_updated

    @staticmethod
    def _get_options_from_player_json(preset_options: BaseOptions, player_json: dict) -> bool:
        if not player_json:
            return False

        settings_updated = False
        player_json_options = player_json.get(preset_options.key, dict())
        for option in preset_options.options:
            if option.key not in player_json_options:
                continue
            option.value = player_json_options.get(option.key)
            option.exists_in_rf = True
            settings_updated = True

        return settings_updated

    def read_player_json_dict(self, file: Path, encoding: Optional[str] = None) -> Optional[dict]:
        if not file.exists() or not file.is_file():
            return

        encoding_ls = ["utf-8", "cp1252"]
        if encoding:
            if encoding in encoding_ls:
                encoding_ls.remove(encoding)
            encoding_ls.append(encoding)

        while encoding_ls:
            encoding = encoding_ls.pop()
            try:
                try:
                    with open(file, "r", encoding=encoding) as f:
                        return json.load(f)
                except UnicodeDecodeError as e:
                    logging.debug("Could not decode JSON data with encoding %s: %s", encoding, e)
                    continue
            except Exception as e:
                msg = f"Could not read {file.name} file! {e}"
                logging.fatal(msg)
                self.error += f"{msg}\n"

    def read_controller_devices(self, controller_json: dict):
        if controller_json:
            self.controller_devices = controller_json.get("Devices", dict())

    def read_dx_ini(self, vr_ini=False) -> Optional[ConfigParser]:
        try:
            # TODO: check that file exists!
            conf = self._create_ini_config_parser()
            ini_file = self.ini_vr_file if vr_ini else self.ini_file
            with open(ini_file, "r") as f:
                self.ini_first_line = f.readline()
                conf.read_file(f)
                return conf
        except Exception as e:
            self.error += f"Could not read CONFIG_DX11.ini file! {e} {self.ini_file}\n"
            logging.fatal(self.error)

    def _read_version(self) -> bool:
        if not self.version_file.exists() or not self.version_file.is_file():
            return False
        try:
            with open(self.version_file, "r") as f:
                self.version = f.readline()
        except Exception as e:
            logging.error("Error reading version file: %s", e)
            return False

        return True

    def _create_ini_config_parser(self):
        config_parser = ConfigParser(**self.config_parser_args)
        config_parser.optionxform = str
        return config_parser

    def _get_location(self):
        RfactorLocation.get_location()
        if not RfactorLocation.is_valid:
            self.error += "Could not locate Le Mans Ultimate installation\n"
            return

        self.location = RfactorLocation.path
        self.player_file = RfactorLocation.player_json
        self.controller_file = RfactorLocation.controller_json
        self.keyboard_file = RfactorLocation.keyboard_json
        self.ini_file = RfactorLocation.dx_config
        self.ini_vr_file = RfactorLocation.dx_vr_config
        self.version_file = RfactorLocation.version_txt

    def _check_bin_dir(self) -> bool:
        return self.location and Path(self.location).exists()

    def run_rfactor(self, method: int = 0, server_info: Optional[dict] = None) -> bool:
        """
            Method:
                0 - Launch via Steam
                1 - Launch via Executable
                2 - Launch via Steam in VR
                3 - Launch via Executable in VR
        :param method:
        :param server_info:
        :return:
        """
        if not self._check_bin_dir():
            self.error += "Could not locate Le Mans Ultimate Bin directory.\n"
            return False

        # Solution for non-loading rF2 plugins in PyInstaller executable:
        #    ctypes.windll.kernel32.SetDllDirectoryA(None)
        # See https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess#windows-dll-loading-order
        executable = self.location / GAME_EXECUTABLE
        if method in (1, 3) and not executable.exists():
            logging.error(f"Could not locate executable: {executable}")
            return False
        if sys.platform != "linux":
            cmd = [str(WindowsPath(executable))]
        else:
            cmd = [executable.as_posix()]

        # -- Use Steam Launch as default
        #    so Workshop items are updated upon start
        if method in (0, 2):
            steam_path = Path(SteamApps.find_steam_location()) / "steam.exe"
            if not steam_path.exists():
                logging.error(f"Could not locate executable: {steam_path}")
                return False
            if sys.platform != "linux":
                cmd = [str(WindowsPath(steam_path)), "-applaunch", LMU_APPID]
            else:
                cmd = [steam_path.as_posix(), "-applaunch", LMU_APPID]

        # -- Add '+VR' Commandline Option
        if method in (2, 3):
            cmd += ["+VR"]

        if server_info:
            ip, port = server_info.get("address", ("localhost",))[0], server_info.get("port", "64297")
            p = server_info.get("password")
            cmd += ["+multiplayer", f'+connect={":" if p else ""}{p}{"@" if p else ""}{ip}:{port}']

        logging.info("Launching %s", cmd)
        subprocess.Popen(cmd, cwd=self.location)
        return True
