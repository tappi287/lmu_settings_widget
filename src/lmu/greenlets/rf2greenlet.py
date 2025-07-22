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


def _rfactor_greenlet_loop():
    global ENABLE_METRICS

    # -- Receive Quit rFactor Event from FrontEnd
    if RfactorQuitEvent.event.is_set():
        CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=10.0))
        CommandQueue.append(Command(Command.quit, timeout=10.0))
        # -- Reset Quit Event
        RfactorQuitEvent.reset()

    # -- Receive Metrics enabled/disabled updates
    if EnableMetricsEvent.event.is_set():
        metrics_enabled = EnableMetricsEvent.get_nowait()
        ENABLE_METRICS = metrics_enabled if metrics_enabled is not None else False
        if not ENABLE_METRICS:
            PerformanceMetricsEvent.set(None)
    # -- Setup PresentMon or report unavailable via Event
    if RfactorConnect.present_mon is None:
        RfactorConnect.present_mon = PresentMon()
        try:
            PresentMonVersionEvent.set(RfactorConnect.present_mon.get_api_version())
        except Exception as e:
            logging.error(f"Error getting PresentMon API Version: {e}")
            PresentMonVersionEvent.set(None)

    # -- While we are live
    if RfactorLiveEvent.was_live and RfactorConnect.rf2_pid:
        # Initialisiere PresentMon wenn noch nicht vorhanden
        if ENABLE_METRICS and not RfactorConnect.present_mon.is_tracking_process:
            try:
                RfactorConnect.present_mon.start(RfactorConnect.rf2_pid)
                logging.info(f"PresentMon for PID {RfactorConnect.rf2_pid} started")
            except Exception as e:
                logging.error(f"Error starting PresentMon Query: {e}")

        # Get PresentMon Metrics and store in AsyncResult
        if ENABLE_METRICS and RfactorConnect.present_mon.is_tracking_process:
            try:
                metrics = RfactorConnect.present_mon.get_metrics()
                if metrics:
                    PerformanceMetricsEvent.set(metrics)
            except Exception as e:
                logging.error(f"Error getting Performance-Metrics: {e}")
        # Stop PresentMon Session if Metrics disabled
        if not ENABLE_METRICS and RfactorConnect.present_mon.is_tracking_process:
            RfactorConnect.present_mon.stop()

    # -- If we were live before
    if RfactorLiveEvent.changed_from_live():
        # -- Report state change to frontend
        RfactorLiveEvent.set(False)
        # -- Stoppe PresentMon wenn rFactor beendet wurde
        if RfactorConnect.present_mon:
            try:
                RfactorConnect.present_mon.stop()
                logging.info("PresentMon stopped, Game no longer running.")
            except Exception as e:
                logging.error(f"Error stopping PresentMon: {e}")

    # -- Report wait for processes shut down
    if RfactorConnect.state == RfactorState.waiting_for_process:
        RfactorStatusEvent.set("Waiting for shut down of rFactor 2 processes.")

    # -- Update rFactor Live State
    if RfactorConnect.state != RfactorState.unavailable and not RfactorLiveEvent.was_live:
        # -- Report state change to frontend
        RfactorLiveEvent.set(True)
        RfactorConnect.set_to_active_timeout()

    # -- Rfactor Live
    if RfactorLiveEvent.get_nowait():
        if not RfactorConnect.rf2_pid:
            RfactorConnect.get_pid()

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
