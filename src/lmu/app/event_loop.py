import logging
import time
from typing import Optional

import eel

from lmu.app.app_main import HEARTBEAT_EVENT, CLOSE_EVENT
from lmu.app_settings import AppSettings
from lmu.rf2events import HardwareStatusEvent
from lmu.crystools.hardware import CHardwareInfo

HEARTBEAT_ENABLED = True


class AppEventLoopGlobals:
    LAST_HEARTBEAT_SEND_TIME = 0.0
    LAST_FRONTEND_HEARTBEAT_TIME = 0.0
    LAST_HW_INFO_PULL_TIME = 10.0

    FRONTEND_TIMEOUT = 60.0
    HEARTBEAT_SEND_INTERVAL = 30.0

    FIRST_RUN = True

    HW_INFO: Optional[CHardwareInfo] = None


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

    # -- Hardware Info
    if AppSettings.show_hardware_info:
        # -- Init Hardware Info Utility
        if AppEventLoopGlobals.HW_INFO is None:
            AppEventLoopGlobals.HW_INFO = CHardwareInfo(True, True, False, True, True)

        # -- Update Hardware Stats in Interval
        if current_time - AppEventLoopGlobals.LAST_HW_INFO_PULL_TIME > AppSettings.HARDWARE_UPDATE_INTERVAL:
            if AppEventLoopGlobals.HW_INFO is not None:
                HardwareStatusEvent.set(AppEventLoopGlobals.HW_INFO.getStatus())
            AppEventLoopGlobals.LAST_HW_INFO_PULL_TIME = current_time
