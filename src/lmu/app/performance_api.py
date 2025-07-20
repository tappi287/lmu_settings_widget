import json
from typing import Optional

import eel
import logging
from lmu.benchmark.present_mon_wrapper import MetricData
from lmu.rf2events import PerformanceMetricsEvent


def expose_performance_api_methods():
    """empty method we import to have the exposed methods registered"""
    pass


@eel.expose
def get_performance_metrics():
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
