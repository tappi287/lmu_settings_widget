import logging
import os
import statistics
import sys
import time
import webbrowser
from pathlib import Path

import eel
import gevent

from lmu import eel_mod
from lmu.app import expose_app_methods
from lmu.app.app_main import CLOSE_EVENT, close_callback, restore_backup
from lmu.app.event_loop import app_event_loop
from lmu.app_settings import AppSettings
from lmu.greenlets.gamecontroller import controller_greenlet, controller_event_loop
from lmu.log import setup_logging
from lmu.greenlets.rf2greenlet import rfactor_event_loop, rfactor_greenlet
from lmu.runasadmin import run_as_admin
from lmu.utils import AppExceptionHook
from lmu.globals import FROZEN, get_current_modules_dir

os.chdir(get_current_modules_dir())

# -- Make sure eel methods are exposed at start-up
expose_app_methods()

# -- Setup logging
setup_logging()

START_TIME = 0.0
SHOW_APP_RUNTIME_STATS = False

# TODO: display purple sector as icons


def in_restore_mode() -> bool:
    """Return True if App is started in Restore Mode"""
    if len(sys.argv) > 1 and sys.argv[1] == "-b":
        logging.warning("Found restore mode argument. Beginning to restore rFactor 2 settings.")
        restore_backup()
        logging.warning("\nFinished Restore Mode. Exiting application.")
        return True
    return False


def prepare_app_start() -> bool:
    """Return True if npm_serve should be used"""
    global START_TIME
    START_TIME = time.time()
    logging.info("\n\n\n")
    logging.info("#######################################################")
    logging.info("################ Starting APP               ###########")
    logging.info("#######################################################\n\n\n")
    logging.info(f"Args: {sys.argv}")

    AppSettings.load()
    AppSettings.copy_default_presets()
    AppSettings.delete_current_settings_presets()

    if FROZEN:
        # Set Exception hook
        sys.excepthook = AppExceptionHook.exception_hook
        return False
    return True


def _main_app_loop():
    # -- Game Controller Greenlet
    cg = gevent.spawn(controller_greenlet)
    # -- Game Greenlet
    rg = gevent.spawn(rfactor_greenlet)

    # -- Run until window/tab closed
    logging.debug("Entering Event Loop")
    run_times, timer_counter = list(), 0

    while not CLOSE_EVENT.is_set():
        try:
            if SHOW_APP_RUNTIME_STATS:
                start_time = time.perf_counter_ns()
                timer_counter += 1

            # Controller event loop
            controller_event_loop()
            # Game Event Loop
            rfactor_event_loop()
            # Capture exception events
            AppExceptionHook.exception_event_loop()
            # App Event loop
            app_event_loop()

            gevent.sleep(AppSettings.TARGET_LOOP_WAIT_HALF)

            if SHOW_APP_RUNTIME_STATS:
                run_times.append(time.perf_counter_ns() - start_time)
                run_times = run_times[-60:]

                if not timer_counter % 20:
                    timer_counter = 0
                    logging.info(f"Median runtimes: {statistics.median(run_times) * 0.000001:.0f}ms")
        except KeyboardInterrupt:
            CLOSE_EVENT.set()

    # -- Shutdown Greenlets
    logging.debug("Shutting down Greenlets.")
    gevent.joinall((cg, rg), timeout=15.0, raise_error=True)


def start_eel(npm_serve=True):
    # This will ask for and re-run with admin rights
    # if setting needs_admin set.
    if AppSettings.needs_admin and not run_as_admin():
        return

    host = "localhost"
    page = "index.html"
    port = 8124

    if npm_serve:
        # Dev env with npm run serve
        page = {"port": 8080}
        url_port = page.get("port")

        eel.init(Path(get_current_modules_dir()).joinpath("vue/src").as_posix())
        # Prepare eel function names cache
        eel_mod.prepare_eel_cache_js()
    else:
        # Frozen or npm run build
        url_port = port
        # Use eel function name cache
        # eel.init(Path(get_current_modules_dir()).joinpath('web').as_posix())
        eel.init(Path(get_current_modules_dir()).joinpath("web").as_posix(), [".jsc"])

    edge_cmd = f"{os.path.expandvars('%PROGRAMFILES(x86)%')}\\Microsoft\\Edge\\Application\\msedge.exe"
    start_url = f"http://{host}:{url_port}"

    try:
        app_module_prefs = getattr(AppSettings, "app_preferences", dict()).get("appModules", list())
        if Path(edge_cmd).exists() and "edge_preferred" in app_module_prefs:
            eel.start(
                page,
                mode="custom",
                host=host,
                port=port,
                block=False,
                cmdline_args=[edge_cmd, "--profile-directory=Default", f"--app={start_url}"],
            )
        else:
            eel.start(page, host=host, port=port, block=False, close_callback=close_callback)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Chromium Edge
        if Path(edge_cmd).exists():
            logging.info("Falling back to Edge Browser")
            eel.start(
                page,
                mode="custom",
                host=host,
                port=port,
                block=False,
                cmdline_args=[edge_cmd, "--profile-directory=Default", f"--app={start_url}"],
            )
        # Fallback to opening a regular browser window
        else:
            logging.info("Falling back to default Web Browser")
            eel.start(page, mode=None, app_mode=False, host=host, port=port, block=False)
            # Open system default web browser
            gevent.spawn_later(1.0, webbrowser.open_new_tab, start_url)

    logging.info(f"App started in {time.time() - START_TIME:.2f} seconds")
    _main_app_loop()


if __name__ == "__main__":
    if not in_restore_mode():
        start_eel(prepare_app_start())

    # -- Shutdown logging
    logging.info("\n\n\n")
    logging.info("#######################################################")
    logging.info("################ APP SHUTDOWN               ###########")
    logging.info("#######################################################\n\n\n")
    logging.shutdown()
