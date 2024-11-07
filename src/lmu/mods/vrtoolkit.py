import logging
import shutil
from pathlib import Path
from typing import Iterator, Tuple
from zipfile import ZipFile

try:
    from pathlib import WindowsPath
    import winreg as registry

    WINREG_AVAIL = True
except ImportError:
    WINREG_AVAIL = False

from lmu.utils import get_registry_values_as_dict
from lmu.globals import get_data_dir, GAME_EXECUTABLE
from lmu.preset.settings_model import BaseOptions, ReshadeClaritySettings
from lmu.settingsdef import graphics


class VrToolKit:
    RESHADE_ZIP = "VRToolkitReshadeUniversal_1.0.2_plus_Clarity.zip"
    RESHADE_PRESET_DIR = "reshade-shaders/Presets/"
    RESHADE_TARGET_PRESET_NAME = "lmu_widget_preset.ini"
    RESHADE_INI_NAME = "ReShadeVR.ini"
    RESHADE_VR_INI_NAME = "ReShadeVR.ini"
    RESHADE_OPENXR_LAYER_DIR = "reshade_openxr_layer"
    RESHADE_OPENXR_LAYER_JSON = "ReShade64_XR.json"
    RESHADE_OPENXR_APPS_INI = "ReShadeApps.ini"
    OPEN_XR_API_LAYER_REG_PATH = "SOFTWARE\\Khronos\\OpenXR\\1\\ApiLayers\\Implicit"

    dll_tgt = ("ReShade64.dll", "dxgi.dll")
    extra_files = [
        ("rF2_nonPBRmodDay1.png", "reshade-shaders/Textures"),
        ("rF2_nonPBRmodDay2.png", "reshade-shaders/Textures"),
        ("rF2_ToneDownDay.png", "reshade-shaders/Textures"),
        ("lut_ams.png", "reshade-shaders/Textures"),
        ("lut_gtr2.png", "reshade-shaders/Textures"),
        ("lut_rbr.png", "reshade-shaders/Textures"),
        ("lut_filmic_basic.png", "reshade-shaders/Textures"),
        ("lut_provia.png", "reshade-shaders/Textures"),
        ("lut_technicolor.png", "reshade-shaders/Textures"),
    ]
    preprocessor_name = "PreprocessorDefinitions"
    preprocessor = {
        "VRT_SHARPENING_MODE": 0,
        "VRT_USE_CENTER_MASK": 0,
        "VRT_DITHERING": 0,
        "VRT_COLOR_CORRECTION_MODE": 0,
        "VRT_ANTIALIASING_MODE": 0,
        "LUT_TextureName": '"lut.png"',
        "ClarityRGBMode": 0,
        "UseClarityDebug": 0,
    }

    techniques_name = "Techniques"
    techniques_sorting = "TechniqueSorting"
    vrt_shader = "VRToolkit.fx"
    vrt_technique = f"VRToolkit@{vrt_shader}"
    clarity2_shader = "Clarity2.fx"
    clarity2_technique = f"Clarity2@{clarity2_shader}"

    def __init__(self, options: Iterator[BaseOptions], location: Path):
        self.options = options
        self.location = location

        self.error = str()
        self.ini_settings = dict()
        self.ini_default_settings = dict()

        self.vr_toolkit_ini_keys = set()
        self.clarity_ini_keys = set()

        self._read_setting_defaults()

    @classmethod
    def reshade_openxr_layer_dir(cls) -> Path:
        return get_data_dir() / cls.RESHADE_OPENXR_LAYER_DIR

    @classmethod
    def reshade_openxr_json_path(cls) -> str:
        return str(WindowsPath(cls.reshade_openxr_layer_dir() / cls.RESHADE_OPENXR_LAYER_JSON))

    @classmethod
    def reshade_openxr_ini_path(cls) -> str:
        return str(WindowsPath(cls.reshade_openxr_layer_dir() / cls.RESHADE_OPENXR_APPS_INI))

    @classmethod
    def update_reshade_openxr_apps_ini(cls, game_executable: Path) -> bool:
        reshade_openxr_ini_path = Path(cls.reshade_openxr_ini_path())
        if not reshade_openxr_ini_path.exists():
            logging.error(f"Could not locate ReShade OpenXR Apps INI file: {reshade_openxr_ini_path}")
            return False

        utf8_bom = b"\xef\xbb\xbf"
        game_executable_win_path = str(WindowsPath(game_executable))

        with open(reshade_openxr_ini_path, "rb") as f:
            data = f.read()

        if data.startswith(utf8_bom):
            text = data[3:].decode("utf-8")
        else:
            text = data.decode("utf-8")

        paths_text, paths = text[5:], list()  # remove Apps=
        if paths_text:
            # Read existing paths
            paths = paths_text.replace("\n", "").replace("\r", "").split(",")
            paths = [p for p in paths if p != ""]

        # Path already in INI
        if game_executable_win_path in paths:
            return True

        # Add path
        paths.append(game_executable_win_path)

        # Write to file
        eof = "\r\n" * 3
        out_text = f"Apps={','.join(paths)}{eof}"

        with open(reshade_openxr_ini_path, "wb") as f:
            out_bytes = utf8_bom
            out_bytes += out_text.encode("utf-8")
            f.write(out_bytes)

        return True

    @classmethod
    def is_openxr_layer_installed(cls) -> int:
        """Check if the ReShade OpenXR API Layer is set up.

        :returns: 0 - if not installed, 1 - installed and active, -1 - installed but deactivated
        """
        if not WINREG_AVAIL:
            logging.error(f"Windows registry not available, can not check OpenXR-API-Layer installation")
            return 0

        # -- Open OpenXR v1 API Layers registry key
        try:
            key = registry.OpenKey(registry.HKEY_CURRENT_USER, cls.OPEN_XR_API_LAYER_REG_PATH)
            values = get_registry_values_as_dict(key)
            if cls.reshade_openxr_json_path() in values:
                value = values.get(cls.reshade_openxr_json_path())
                if value.get("data") == 0:
                    return 1
                else:
                    return -1
        except OSError as e:
            logging.error(f"Could not open or create registry key: {e}")
            return 0

    @classmethod
    def remove_reshade_openxr_layer(cls) -> bool:
        if not WINREG_AVAIL:
            logging.error(f"Windows registry not available, skipping OpenXR-API-Layer setup")
            return False

        # -- Open OpenXR v1 API Layers registry key
        layer_present = False
        try:
            key = registry.OpenKey(
                registry.HKEY_CURRENT_USER, cls.OPEN_XR_API_LAYER_REG_PATH, access=registry.KEY_ALL_ACCESS
            )
            if cls.reshade_openxr_json_path() in get_registry_values_as_dict(key):
                layer_present = True
        except OSError as e:
            logging.error(f"Could not read registry key: {e}")
            return False

        if layer_present:
            registry.DeleteValue(key, cls.reshade_openxr_json_path())
        return True

    @classmethod
    def setup_reshade_openxr_layer(cls, enable=True, game_executable: Path = None) -> bool:
        """Setup ReShade via it's OpenXR-API-Layer
            this will end up in HKEY_CURRENT_USER\SOFTWARE\Khronos\OpenXR\1\ApiLayers\Implicit

            https://registry.khronos.org/OpenXR/specs/1.0/loader.html#windows-manifest-registry-usage

        :return:
        """
        if not WINREG_AVAIL:
            logging.error(f"Windows registry not available, skipping OpenXR-API-Layer setup")
            return False

        # -- Update ReShade Apps INI
        if game_executable is not None:
            cls.update_reshade_openxr_apps_ini(game_executable)

        # -- Open or create OpenXR v1 API Layers registry key
        try:
            key = registry.CreateKey(registry.HKEY_CURRENT_USER, VrToolKit.OPEN_XR_API_LAYER_REG_PATH)
        except OSError as e:
            logging.error(f"Could not open or create registry key: {e}")
            return False

        # -- Get the path to reshade openxr dir which is equal to the name of the value
        reshade_path_value = VrToolKit.reshade_openxr_json_path()

        # -- Get existing values
        existing_values = get_registry_values_as_dict(key)

        # Layer already setup
        if reshade_path_value in existing_values:
            reshade_layer_enabled = existing_values[reshade_path_value]["data"] == 0
            if reshade_layer_enabled and enable:
                logging.debug(
                    f"Reshade OpenXR API Layer already enabled: " f"{existing_values[reshade_path_value]['data']}"
                )
                return True

        # -- Set DWORD value to 0 to enable the layer or non-zero to disable the layer
        try:
            registry.SetValueEx(key, reshade_path_value, 0, registry.REG_DWORD, 0 if enable else 1)
        except OSError as e:
            logging.error(f"Could not set ReShade OpenXR API Layer value: {e}")
            return False

        return True

    def _read_setting_defaults(self):
        settings_dict = dict()
        settings_dict.update(graphics.reshade_fas)
        settings_dict.update(graphics.reshade_dither)
        settings_dict.update(graphics.reshade_mask)
        settings_dict.update(graphics.reshade_aa)
        settings_dict.update(graphics.reshade_cas)
        settings_dict.update(graphics.reshade_cc)
        settings_dict.update(graphics.reshade_lut)
        self.vr_toolkit_ini_keys = set(settings_dict.keys())

        settings_dict.update(graphics.reshade_clarity)
        self.clarity_ini_keys = set(graphics.reshade_clarity.keys())

        for key, setting in settings_dict.items():
            self.ini_settings[key] = setting.get("value")
            self.ini_default_settings[key] = setting.get("value")

    def _update_options(self, update_from_disk=False, clarity_found=True) -> Tuple[bool, bool, bool]:
        use_reshade, use_openxr, use_clarity = False, False, False

        # -- Iterate Preset options
        for preset_options in self.options:
            # -- Exclude Clarity settings that will not be in Ini if disabled
            if preset_options.app_key == ReshadeClaritySettings.app_key and not use_clarity:
                for option in preset_options.options:
                    option.exists_in_rf = False
                continue

            for option in preset_options.options:
                # -- Read from Preset options
                if not update_from_disk:
                    if option.key == "use_reshade":
                        use_reshade = option.value
                    elif option.key == "use_openxr":
                        use_openxr = option.value
                    elif option.key == "use_clarity":
                        use_clarity = option.value
                    elif option.key in self.preprocessor:
                        self.preprocessor[option.key] = option.value
                    elif option.key in self.ini_settings:
                        self.ini_settings[option.key] = option.value
                # -- Read from disk and update Preset options
                else:
                    if option.key == "use_reshade":
                        option.value = True
                        option.exists_in_rf = True
                    if option.key == "use_openxr":
                        option.value = self.is_openxr_layer_installed() == 1
                        option.exists_in_rf = True
                    if option.key == "use_clarity":
                        option.value = clarity_found
                        option.exists_in_rf = True
                    elif option.key in self.preprocessor:
                        option.value = self.preprocessor[option.key]
                        option.exists_in_rf = True
                    elif option.key in self.ini_settings:
                        option.value = self.ini_settings[option.key]
                        option.exists_in_rf = True

        return use_reshade, use_clarity, use_openxr

    def _work_thru_reshade_release_zip(self, use_reshade: bool, use_openxr: bool, bin_dir: Path) -> list:
        reshade_zip = get_data_dir() / self.RESHADE_ZIP
        remove_dirs = list()

        def _remove_reshade_dll(in_file: Path):
            dll_file = Path(in_file.parent / self.dll_tgt[1])
            if dll_file.is_file():
                dll_file.unlink(missing_ok=True)
                logging.info("Removing ReShade file %s from game bin dir.", dll_file)

        with ZipFile(reshade_zip, "r") as zip_obj:
            for zip_info in zip_obj.filelist:
                file = bin_dir / zip_info.filename

                # -- Extract Zip member
                if use_reshade:
                    # -- Remove dll if OpenXR is in use
                    if self.dll_tgt[0] == zip_info.filename and use_openxr:
                        _remove_reshade_dll(file)
                        continue

                    # -- Skip existing files
                    if file.exists():
                        continue

                    logging.info("Extracting ReShade file %s to rF2 bin dir.", file)
                    zip_obj.extract(zip_info, path=bin_dir)

                    # - ReShade64.dll -> dxgi.dll
                    if self.dll_tgt[0] == zip_info.filename:
                        new_file = bin_dir / self.dll_tgt[1]
                        new_file.unlink(missing_ok=True)
                        try:
                            file.rename(new_file)
                        except Exception as e:
                            logging.error("Could not rename file: %s", e)
                # -- Remove files found in zip
                else:
                    # - Remove renamed dll
                    _remove_reshade_dll(file)

                    # - Remove files matching zip file
                    if file.is_file():
                        logging.info("Removing ReShade file %s from rF2 bin dir.", file)
                        file.unlink(missing_ok=True)
                    else:
                        if file.exists():
                            remove_dirs.append(file)

        # -- Copy/Remove extra files
        for file_name, file_target_dir in self.extra_files:
            src_file = get_data_dir() / file_name
            target_file = bin_dir / file_target_dir / file_name

            try:
                # -- Copy file
                if use_reshade:
                    shutil.copyfile(src_file, target_file)
                # -- Remove file
                else:
                    target_file.unlink(missing_ok=True)
            except Exception as e:
                logging.error("Could not process extra file %s: %s", file_name, e)

        return remove_dirs

    @staticmethod
    def _add_ini_value_line(key, value):
        if isinstance(value, (str, int)):
            return f"{key}={value}\n"
        else:
            return f"{key}={value:.6f}\n"

    def _update_preset_ini(self, reshade_preset: Path, use_clarity=False):
        """Write updated values to custom VRToolKit Preset"""
        p_dict, preprocessor_values = self.preprocessor.copy(), ""

        # -- Prepare Preprocessor values
        for k, v in p_dict.items():
            preprocessor_values += f'{"," if preprocessor_values else ""}{k}={v}'

        # -- Update Preset Ini file
        try:
            # -- Create Preset Ini Settings
            configured_preset_lines = list()
            configured_preset_lines.append(f"{self.preprocessor_name}={preprocessor_values}\n")
            configured_preset_lines.append(
                f"{self.techniques_name}={self.vrt_technique}"
                f'{f",{self.clarity2_technique}" if use_clarity else ""}\n'
            )
            configured_preset_lines.append(
                f"{self.techniques_sorting}={self.vrt_technique}"
                f'{f",{self.clarity2_technique}" if use_clarity else ""}\n'
            )

            # -- Add [Clarity2.fx] Ini Settings
            clarity_fx_lines = list()
            for k, v in self.ini_settings.items():
                if k not in self.clarity_ini_keys or v == self.ini_default_settings.get(k):
                    continue
                clarity_fx_lines.append(self._add_ini_value_line(k, v))

            if use_clarity:
                configured_preset_lines.append("\n")
                configured_preset_lines.append(f"[{self.clarity2_shader}]\n")
                configured_preset_lines.extend(clarity_fx_lines)
                configured_preset_lines.append("\n")

            # -- Add [VRToolkit.fx] Ini Settings
            configured_preset_lines.append("\n")
            configured_preset_lines.append(f"[{self.vrt_shader}]\n")
            for k, v in self.ini_settings.items():
                if k not in self.vr_toolkit_ini_keys or v == self.ini_default_settings.get(k):
                    continue
                configured_preset_lines.append(self._add_ini_value_line(k, v))

            # - Write Preset Ini file
            logging.info("Creating ReShade Preset file: %s", reshade_preset)
            with open(reshade_preset, "w") as f:
                f.writelines(configured_preset_lines)

            for line in configured_preset_lines:
                logging.debug("Updated VRToolkit Setting: %s", line.replace("\r", "").replace("\n", ""))
        except Exception as e:
            msg = f"Error writing Reshade Preset Ini file: {e}"
            logging.error(msg)
            self.error = msg
            return False
        return True

    @staticmethod
    def _update_reshade_ini(base_dir: Path, vr_ini=False):
        """update the global reshade preset ini to update preset path"""
        reshade_preset_dir_str = VrToolKit.RESHADE_PRESET_DIR.replace("/", "\\")
        reshade_preset_path = f".\\{reshade_preset_dir_str}{VrToolKit.RESHADE_TARGET_PRESET_NAME}"
        reshade_ini = base_dir / VrToolKit.RESHADE_VR_INI_NAME if vr_ini else base_dir / VrToolKit.RESHADE_INI_NAME

        reshade_ini_lines, updated_ini_lines = list(), list()

        # -- Read current ReShade.ini
        with open(reshade_ini, "r") as f:
            reshade_ini_lines = f.readlines()

        for line in reshade_ini_lines:
            if line.startswith("PresetPath="):
                line = f"PresetPath={reshade_preset_path}\n"
            # -- VRToolkit default setting seems to set this to 1 which results in
            #    settings updates not being applied on start up
            if line.startswith("NoReloadOnInitForNonVR"):
                line = "NoReloadOnInitForNonVR=0\n"
            updated_ini_lines.append(line)

        # -- Write updated ReShade.ini
        with open(reshade_ini, "w") as f:
            f.writelines(updated_ini_lines)

    def write(self):
        use_reshade, use_clarity, use_openxr = self._update_options()

        bin_dir = self.location
        reshade_preset = bin_dir / self.RESHADE_PRESET_DIR / self.RESHADE_TARGET_PRESET_NAME
        reshade_removed = False

        # -- Extract ReShade files
        logging.info("Applying ReShade settings: %s", use_reshade)
        remove_dirs = self._work_thru_reshade_release_zip(use_reshade, use_openxr, bin_dir)

        # -- Remove ReShade directories and files
        if not use_reshade:
            # -- Disable OpenXR API Layer
            if use_openxr:
                if self.is_openxr_layer_installed() == 1:
                    self.setup_reshade_openxr_layer(enable=False)

            # -- Remove ReShade preset
            if reshade_preset.exists():
                reshade_preset.unlink()

            # -- Remove empty ReShade dirs
            if remove_dirs:
                for d in sorted(remove_dirs, key=lambda x: len(x.as_posix()), reverse=True):
                    try:
                        d.rmdir()
                    except Exception as e:
                        # Eg. if the use has saved screenshots, directory will not be removed
                        msg = f"Will not delete ReShade directory with user data: {e}"
                        logging.error(msg)
                        self.error += msg

            return reshade_removed

        # -- Update global ReShade.ini
        self._update_reshade_ini(bin_dir, True)
        self._update_reshade_ini(bin_dir)

        # -- Enable OpenXR API Layer
        if use_openxr:
            game_executable_path = bin_dir / GAME_EXECUTABLE
            self.setup_reshade_openxr_layer(True, game_executable_path)

        # -- Prepare writing of ReShade Preset file
        return self._update_preset_ini(reshade_preset, use_clarity)

    def _read_preset_ini(self, reshade_preset: Path) -> bool:
        """Lookup current VRToolkit Settings on disk"""
        if not reshade_preset.exists():
            return False

        try:
            # - Read Preset Ini file
            with open(reshade_preset, "r") as f:
                preset_lines = f.readlines()

            # - Read settings from Preset Ini file lines
            clarity_found = False
            for line in preset_lines:
                if line.startswith(self.preprocessor_name):
                    p_str = line.replace(f"{self.preprocessor_name}=", "").replace("\n", "")
                    for p_def in p_str.split(","):
                        key, value = p_def.split("=", 2)
                        if key in self.preprocessor:
                            if value.isnumeric():
                                self.preprocessor[key] = int(value)
                            else:
                                self.preprocessor[key] = value
                if line.startswith(self.techniques_name) and self.clarity2_technique in line:
                    clarity_found = True
                for k, v in self.ini_settings.items():
                    splitted_line = line.split("=", 1)
                    if len(splitted_line) == 2:
                        line_key, value = line.split("=", 1)
                    else:
                        continue
                    if line_key == k:
                        if isinstance(value, str) and value.split(".")[0].isnumeric():
                            # -- Read int
                            if value.isdigit():
                                self.ini_settings[k] = int(value)
                            # -- Read float
                            else:
                                self.ini_settings[k] = float(value)
                        else:
                            # -- Read str
                            self.ini_settings[k] = value

            # -- Update RfactorPlayer VRToolkit Settings
            self._update_options(update_from_disk=True, clarity_found=clarity_found)
        except Exception as e:
            msg = f"Error reading Reshade Preset Ini file: {e}"
            logging.exception(msg, exc_info=e)
            self.error = msg
            return False
        return True

    def read(self) -> bool:
        bin_dir = self.location
        reshade_preset = bin_dir / self.RESHADE_PRESET_DIR / self.RESHADE_TARGET_PRESET_NAME

        return self._read_preset_ini(reshade_preset)
