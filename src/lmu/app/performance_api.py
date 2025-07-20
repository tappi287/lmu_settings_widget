import json
from typing import Optional

import eel
import logging
from lmu.present_mon_wrapper import MetricData
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
        metrics_dict = {
            # FPS Metriken
            "fps_avg": metrics.fps_avg,
            "fps_90": metrics.fps_90,
            "fps_95": metrics.fps_95,
            "fps_99": metrics.fps_99,
            "fps_max": metrics.fps_max,
            "fps_min": metrics.fps_min,
            # Frametimes und Performance
            "frame_duration_avg": metrics.frame_duration_avg,
            "frame_pacing_stall_avg": metrics.frame_pacing_stall_avg,
            "gpu_time_avg": metrics.gpu_time_avg,
            "gpu_busy_avg": metrics.gpu_busy_avg,
            "cpu_frame_time_avg": metrics.cpu_frame_time_avg,
            # Latenz
            "display_latency_avg": metrics.display_latency_avg,
            "display_duration_avg": metrics.display_duration_avg,
            "input_latency_avg": metrics.input_latency_avg,
            # Hardware-Metriken
            "gpu_power_avg": metrics.gpu_power_avg,
            # CPU-Metriken
            "cpu_utilization": metrics.cpu_utilization,
            "cpu_frequency": metrics.cpu_frequency,
        }

        return json.dumps(metrics_dict)
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Performance-Metriken: {e}")
        return json.dumps({})
