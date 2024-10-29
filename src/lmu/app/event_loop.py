import logging
import time

import eel

from lmu.app.app_main import HEARTBEAT_EVENT, CLOSE_EVENT

HEARTBEAT_ENABLED = True


class AppEventLoopGlobals:
    LAST_HEARTBEAT_SEND_TIME = 0.0
    LAST_FRONTEND_HEARTBEAT_TIME = 0.0

    FRONTEND_TIMEOUT = 60.0
    HEARTBEAT_SEND_INTERVAL = 30.0

    FIRST_RUN = True


def app_event_loop():
    current_time = time.time()

    if HEARTBEAT_ENABLED:
        if AppEventLoopGlobals.FIRST_RUN:
            AppEventLoopGlobals.LAST_HEARTBEAT_SEND_TIME = current_time
            AppEventLoopGlobals.LAST_FRONTEND_HEARTBEAT_TIME = current_time
            AppEventLoopGlobals.FIRST_RUN = False

        # Send heartbeat to FrontEnd
        if current_time - AppEventLoopGlobals.LAST_HEARTBEAT_SEND_TIME > AppEventLoopGlobals.HEARTBEAT_SEND_INTERVAL:
            AppEventLoopGlobals.LAST_HEARTBEAT_SEND_TIME = current_time
            eel.heartbeat()

        # Close the Python application if the frontend no longer seems to be alive
        if HEARTBEAT_EVENT.is_set():
            AppEventLoopGlobals.LAST_FRONTEND_HEARTBEAT_TIME = time.time()
            HEARTBEAT_EVENT.clear()
        if current_time - AppEventLoopGlobals.LAST_FRONTEND_HEARTBEAT_TIME > AppEventLoopGlobals.FRONTEND_TIMEOUT:
            logging.warning(
                f"App did not receive frontend heartbeat within {AppEventLoopGlobals.FRONTEND_TIMEOUT}s "
                f"and will close."
            )
            CLOSE_EVENT.set()
