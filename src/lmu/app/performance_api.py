import json
from typing import Optional

import eel
import logging
from lmu.present_mon_wrapper import PresentMon, MetricData

# Singleton-Instanz des PresentMonWrapper
PRESENT_MON: Optional[PresentMon] = None


def expose_performance_api_methods():
    """empty method we import to have the exposed methods registered"""
    pass


@eel.expose
def init_performance_monitor(pid=None):
    """
    Initialisiert den Performance-Monitor für eine bestimmte Prozess-ID.

    Args:
        pid (int, optional): Die Prozess-ID der zu überwachenden Anwendung. Falls None, wird
                            die aktive Anwendung automatisch erkannt.

    Returns:
        bool: True, wenn die Initialisierung erfolgreich war, sonst False
    """
    global PRESENT_MON

    try:
        # Bestehende Instanz beenden, falls vorhanden
        if PRESENT_MON is not None:
            PRESENT_MON.stop()

        # Neue Instanz erstellen und starten
        PRESENT_MON = PresentMon()
        success = PRESENT_MON.start(pid)

        return success
    except Exception as e:
        logging.error(f"Fehler bei der Initialisierung des Performance-Monitors: {e}")
        return False


@eel.expose
def stop_performance_monitor():
    """
    Stoppt den Performance-Monitor.

    Returns:
        bool: True, wenn das Stoppen erfolgreich war, sonst False
    """
    global PRESENT_MON

    try:
        if PRESENT_MON is not None:
            PRESENT_MON.stop()
            PRESENT_MON = None
        return True
    except Exception as e:
        logging.error(f"Fehler beim Stoppen des Performance-Monitors: {e}")
        return False


@eel.expose
def get_performance_metrics():
    """
    Ruft die aktuellen Performance-Metriken ab.

    Returns:
        str: JSON-String mit den Performance-Metriken oder leerer String bei Fehler
    """
    global PRESENT_MON

    try:
        if PRESENT_MON is None:
            return json.dumps({})

        metrics = PRESENT_MON.get_metrics()
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
