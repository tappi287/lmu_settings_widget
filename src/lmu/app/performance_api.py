import json
from typing import Optional

import eel
import logging
from lmu.benchmark.present_mon_wrapper import MetricData
from lmu.rf2events import PerformanceMetricsEvent, HardwareStatusEvent, PresentMonVersionEvent

from lmu.utils import capture_app_exceptions


def expose_performance_api_methods():
    """empty method we import to have the exposed methods registered"""
    pass


@capture_app_exceptions
def _get_performance_metrics():
    """
    Ruft die aktuellen Performance-Metriken aus dem AsyncResult ab.

    Returns:
        str: JSON-String mit den Performance-Metriken oder leerer String bei Fehler
    """
    try:
        # Nicht-blockierender Abruf der Metriken
        metrics: Optional[MetricData] = PerformanceMetricsEvent.get_nowait()

        if metrics is None:
            return json.dumps({})

        # Konvertiere die MetricData-Instanz in ein Dictionary
        metrics_dict = metrics.to_js_object()

        return json.dumps(metrics_dict)
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Performance-Metriken: {e}")
        return json.dumps({})


@eel.expose
def get_performance_metrics():
    return _get_performance_metrics()


@capture_app_exceptions
def _get_hardware_status():
    hardware_stats = HardwareStatusEvent.get_nowait()
    if hardware_stats is None:
        return json.dumps({"result": False})
    return json.dumps({"result": True, "data": hardware_stats})


@eel.expose
def get_hardware_status():
    return _get_hardware_status()


@capture_app_exceptions
def _get_present_mon_api_version():
    result = PresentMonVersionEvent.get_nowait()
    version = None
    if result is not None:
        version = f"{result[0]}.{result[1]}.{result[2]}"

    return json.dumps({"result": True if result else False, "data": version})


@eel.expose
def get_present_mon_api_version():
    return _get_present_mon_api_version()
