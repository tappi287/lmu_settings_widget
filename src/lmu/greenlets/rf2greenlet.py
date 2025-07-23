"""Connect to rFactor 2 Ui via it's rest api"""

import logging

import eel
import gevent

from lmu.app.app_main import CLOSE_EVENT
from lmu.benchmark import RfactorBenchmark
from lmu.rf2command import Command, CommandQueue
from lmu.rf2connect import RfactorState, RfactorConnect
from lmu.rf2events import (
    RfactorLiveEvent,
    RfactorQuitEvent,
    RfactorStatusEvent,
    BenchmarkProgressEvent,
    EnableMetricsEvent,
    PerformanceMetricsEvent,
    PresentMonVersionEvent,
)
from lmu.benchmark.present_mon_wrapper import PresentMon
from lmu.utils import capture_app_exceptions

ENABLE_METRICS = False
PRESENT_MON_RETRIES = 0
MAX_PRESENT_MON_RETRIES = 5


def _while_rfactor_is_live():
    """Task's while rFactor is live and running"""
    global PRESENT_MON_RETRIES
    if not RfactorConnect.rf2_pid:
        PRESENT_MON_RETRIES = 0
        RfactorConnect.get_pid()

    # -- init PresentMon
    if ENABLE_METRICS and not RfactorConnect.present_mon.is_tracking_process:
        if RfactorConnect.rf2_pid is not None and PRESENT_MON_RETRIES < MAX_PRESENT_MON_RETRIES:
            try:
                if not RfactorConnect.present_mon.start(RfactorConnect.rf2_pid):
                    PRESENT_MON_RETRIES += 1
                    RfactorConnect.present_mon.stop()
                logging.info(f"PresentMon for PID {RfactorConnect.rf2_pid} started")
            except Exception as e:
                logging.error(f"Error starting PresentMon Query: {e}")

    # -- Get PresentMon Metrics and store in AsyncResult
    if ENABLE_METRICS and RfactorConnect.present_mon.is_tracking_process:
        try:
            metrics = RfactorConnect.present_mon.get_metrics()
            if metrics:
                PerformanceMetricsEvent.set(metrics)
        except Exception as e:
            logging.error(f"Error getting Performance-Metrics: {e}")

    # -- Stop PresentMon Session if Metrics disabled
    if not ENABLE_METRICS and RfactorConnect.present_mon.is_tracking_process:
        RfactorConnect.present_mon.stop()


def _rfactor_changed_from_live():
    """rFactor ended and was running before"""
    # -- Report state change to frontend
    RfactorLiveEvent.set(False)
    # -- Stop PresentMon if rFactor ended
    if RfactorConnect.present_mon:
        try:
            RfactorConnect.present_mon.stop()
            logging.info("PresentMon stopped, Game no longer running.")
        except Exception as e:
            logging.error(f"Error stopping PresentMon: {e}")


def _check_and_setup_performance_metrics():
    """Receive Metrics enable/disable events and setup PresentMon instance if not present"""
    global ENABLE_METRICS

    # -- Receive Metrics enabled/disabled updates
    if EnableMetricsEvent.event.is_set():
        metrics_enabled = EnableMetricsEvent.get_nowait()
        ENABLE_METRICS = metrics_enabled if metrics_enabled is not None else False
        if not ENABLE_METRICS:
            PerformanceMetricsEvent.set(None)
        EnableMetricsEvent.reset()

    # -- Setup PresentMon or report unavailable via Event
    if RfactorConnect.present_mon is None:
        RfactorConnect.present_mon = PresentMon()
        try:
            # -- Report version
            PresentMonVersionEvent.set(RfactorConnect.present_mon.get_api_version())
        except Exception as e:
            logging.error(f"Error getting PresentMon API Version: {e}")
            # -- Report unavailable
            PresentMonVersionEvent.set(None)


def _rfactor_greenlet_loop():
    # -- Receive Quit rFactor Event from FrontEnd
    if RfactorQuitEvent.event.is_set():
        CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))
        CommandQueue.append(Command(Command.quit, timeout=10.0))
        # -- Reset Quit Event
        RfactorQuitEvent.reset()

    _check_and_setup_performance_metrics()

    # -- While we are live
    if RfactorLiveEvent.was_live:
        _while_rfactor_is_live()

    # -- If we were live before
    if RfactorLiveEvent.changed_from_live():
        _rfactor_changed_from_live()

    # -- Report wait for processes shut down
    if RfactorConnect.state == RfactorState.waiting_for_process:
        RfactorStatusEvent.set("Waiting for shut down of rFactor 2 processes.")

    # -- Update rFactor Live State
    if RfactorConnect.state != RfactorState.unavailable and not RfactorLiveEvent.was_live:
        # -- Report state change to frontend
        RfactorLiveEvent.set(True)
        RfactorConnect.set_to_active_timeout()

    # ---------------------------
    # -- COMMAND QUEUE
    # ---------------------------
    CommandQueue.run()


@capture_app_exceptions
def rfactor_greenlet():
    logging.info("rFactor Greenlet started.")
    RfactorConnect.start_request_thread()
    rfb = RfactorBenchmark()

    while True:
        # -- App functionality
        _rfactor_greenlet_loop()
        # -- Benchmark functionality
        rfb.event_loop()

        if CLOSE_EVENT.is_set():
            logging.info("rFactor Greenlet received CLOSE event.")
            break

        gevent.sleep(RfactorConnect.active_timeout * 0.25)

    # PresentMon stoppen, falls noch aktiv
    if RfactorConnect.present_mon:
        try:
            RfactorConnect.present_mon.stop()
            RfactorConnect.present_mon = None
            logging.info("PresentMon beim Beenden des Greenlets gestoppt")
        except Exception as e:
            logging.error(f"Fehler beim Stoppen von PresentMon: {e}")

    RfactorConnect.stop_request_thread()
    logging.info("rFactor Greenlet exiting")


@capture_app_exceptions
def rfactor_event_loop():
    """Will be run in main eel greenlet to be able to post events to JS frontend"""
    if RfactorLiveEvent.event.is_set():
        is_live = RfactorLiveEvent.get_nowait()
        # -- Update rFactor live state to front end
        if is_live is not None:
            eel.rfactor_live(is_live)
        RfactorLiveEvent.reset()

    if RfactorStatusEvent.event.is_set():
        status = RfactorStatusEvent.get_nowait()
        # -- Update rFactor status message in front end
        if status is not None:
            eel.rfactor_status(status)
        RfactorStatusEvent.reset()

    if BenchmarkProgressEvent.event.is_set():
        progress = BenchmarkProgressEvent.get_nowait()
        if progress is not None:
            eel.benchmark_progress(progress)
        BenchmarkProgressEvent.reset()
