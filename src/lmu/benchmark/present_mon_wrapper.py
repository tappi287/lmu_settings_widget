import ctypes
import logging
import struct
from ctypes import c_void_p, c_uint32, byref, c_double, c_uint64
from typing import Tuple, Optional

from lmu.globals import get_present_mon_service_loader
from lmu.utils import JsonRepr
from lmu.benchmark import present_mon_const as const


class MetricData(JsonRepr):
    """
    Speichert alle erfassten PresentMon-Metriken.
    """

    def __init__(self):
        # FPS Metriken
        self.fps_avg = 0.0
        self.fps_01 = 0.0
        self.fps_95 = 0.0
        self.fps_99 = 0.0
        self.fps_max = 0.0
        self.fps_min = 0.0

        # Frametimes und Performance
        self.frame_duration_avg = 0.0
        self.frame_pacing_stall_avg = 0.0
        self.gpu_time_avg = 0.0
        self.gpu_busy_avg = 0.0
        self.cpu_frame_time_avg = 0.0
        self.cpu_busy_avg = 0.0

        # Latenz
        self.display_latency_avg = 0.0
        self.display_duration_avg = 0.0
        self.input_latency_avg = 0.0

        # Hardware-Metriken
        self.gpu_power_avg = 0.0
        # CPU-Metriken
        self.cpu_frequency = 0.0
        self.cpu_utilization = 0.0

    def metrics_cpu_frequency(self):
        """Gibt eine lesbare CPU-Frequenz zurück, auch wenn der Wert ungültig ist."""
        if self.cpu_frequency <= 0.0:
            return "Nicht verfügbar"
        return f"{self.cpu_frequency:.2f} GHz"

    def __str__(self):
        return f"""Metriken:
        FPS: {self.fps_avg:.2f} (01%: {self.fps_01:.2f}, 95%: {self.fps_95:.2f}, 99%: {self.fps_99:.2f})
        Frame-Zeit: {self.frame_duration_avg:.2f} ms (CPU: {self.cpu_frame_time_avg:.2f} ms, GPU: {self.gpu_time_avg:.2f} ms)
        Stall: {self.frame_pacing_stall_avg:.2f} ms, GPU Busy: {self.gpu_busy_avg:.2f}%
        Display-Latenz: {self.display_latency_avg:.2f} ms, Input-Latenz: {self.input_latency_avg:.2f} ms
        GPU-Leistung: {self.gpu_power_avg:.2f}W
        CPU: {self.cpu_utilization:.1f}%, Frequenz: {self.metrics_cpu_frequency()}"""


class PresentMon:
    """
    Ein Wrapper für die PresentMon-API, um GPU- und CPU-Frametimes zu überwachen.
    """

    def __init__(self):
        self.pm_dll = None
        self.session = c_void_p()
        self.query = c_void_p()
        self.pid = 0
        self.metrics = MetricData()

        try:
            self.pm_dll = ctypes.WinDLL(str(get_present_mon_service_loader()))
            self._define_api_functions()
            logging.info("PresentMonAPI2Loader.dll erfolgreich geladen.")
        except (OSError, AttributeError) as e:
            logging.error(f"Fehler beim Laden oder Initialisieren von PresentMonAPI2Loader.dll: {e}")
            raise

    def _define_api_functions(self):
        """Definiert die Signaturen der benötigten API-Funktionen."""
        self.pm_dll.pmOpenSession.argtypes = [ctypes.POINTER(c_void_p)]
        self.pm_dll.pmOpenSession.restype = c_uint32

        self.pm_dll.pmCloseSession.argtypes = [c_void_p]
        self.pm_dll.pmCloseSession.restype = c_uint32

        self.pm_dll.pmStartTrackingProcess.argtypes = [c_void_p, c_uint32]
        self.pm_dll.pmStartTrackingProcess.restype = c_uint32

        self.pm_dll.pmRegisterDynamicQuery.argtypes = [
            c_void_p,
            ctypes.POINTER(c_void_p),
            ctypes.POINTER(const.PM_QUERY_ELEMENT),
            c_uint64,
            c_double,
            c_double,
        ]
        self.pm_dll.pmRegisterDynamicQuery.restype = c_uint32

        self.pm_dll.pmPollDynamicQuery.argtypes = [
            c_void_p,
            c_uint32,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(c_uint32),
        ]
        self.pm_dll.pmPollDynamicQuery.restype = c_uint32

        self.pm_dll.pmFreeDynamicQuery.argtypes = [c_void_p]
        self.pm_dll.pmFreeDynamicQuery.restype = c_uint32

        self.pm_dll.pmGetApiVersion.argtypes = [
            ctypes.POINTER(const.PM_VERSION),
        ]
        self.pm_dll.pmGetApiVersion.restype = c_uint32

    @property
    def is_tracking_process(self) -> bool:
        if not self.session or not self.query:
            return False
        return True

    def start(self, process_id: int, window_size_ms: float = 1000.0, metric_offset: float = 500.0) -> bool:
        """
        Startet eine Überwachungssitzung für eine gegebene Prozess-ID.

        Args:
            process_id: Process ID
            window_size_ms: Window size used for metrics calculation eg. 99% percentile
            metric_offset: Offset from top for frame data
        Returns:
            True if tracking process was started, False otherwise
        """
        if not self.pm_dll:
            return False

        self.pid = process_id
        status = self.pm_dll.pmOpenSession(byref(self.session))
        if status != const.PM_STATUS_SUCCESS:
            logging.error(f"pmOpenSession fehlgeschlagen mit Status: {status}")
            return False

        status = self.pm_dll.pmStartTrackingProcess(self.session, self.pid)
        if status != const.PM_STATUS_SUCCESS:
            logging.error(f"pmStartTrackingProcess fehlgeschlagen mit Status: {status}")
            self.pm_dll.pmCloseSession(self.session)
            return False

        # Erstellen einer Liste von Query-Elementen für alle gewünschten Metriken
        metric_configs = [
            # FPS Metriken
            (const.PM_METRIC_PRESENTED_FPS, const.PM_STAT_AVG),  # fps_avg
            (const.PM_METRIC_PRESENTED_FPS, const.PM_STAT_PERCENTILE_01),  # fps_90
            (const.PM_METRIC_PRESENTED_FPS, const.PM_STAT_PERCENTILE_95),  # fps_95
            (const.PM_METRIC_PRESENTED_FPS, const.PM_STAT_PERCENTILE_99),  # fps_99
            (const.PM_METRIC_PRESENTED_FPS, const.PM_STAT_MAX),  # fps_max
            (const.PM_METRIC_PRESENTED_FPS, const.PM_STAT_MIN),  # fps_min
            # Frametimes und Performance
            (const.PM_METRIC_CPU_FRAME_TIME, const.PM_STAT_AVG),  # frame_duration_avg
            (const.PM_METRIC_CPU_BUSY, const.PM_STAT_AVG),  # frame_pacing_stall_avg
            (const.PM_METRIC_CPU_WAIT, const.PM_STAT_AVG),  # frame_pacing_stall_avg
            (const.PM_METRIC_GPU_TIME, const.PM_STAT_AVG),  # gpu_time_avg
            (const.PM_METRIC_GPU_BUSY, const.PM_STAT_AVG),  # gpu_busy_avg
            # Latenz
            (const.PM_METRIC_DISPLAY_LATENCY, const.PM_STAT_AVG),  # display_latency_avg
            (const.PM_METRIC_DISPLAYED_TIME, const.PM_STAT_AVG),  # display_duration_avg
            (const.PM_METRIC_CLICK_TO_PHOTON_LATENCY, const.PM_STAT_NON_ZERO_AVG),  # input_latency_avg
            # Hardware-Metriken
            (const.PM_METRIC_GPU_POWER, const.PM_STAT_AVG),  # gpu_power_avg
            # CPU-Metriken
            (const.PM_METRIC_CPU_UTILIZATION, const.PM_STAT_AVG),  # cpu_utilization
            (const.PM_METRIC_CPU_FREQUENCY, const.PM_STAT_AVG),  # cpu_frequency
        ]

        num_elements = len(metric_configs)
        elements = (const.PM_QUERY_ELEMENT * num_elements)()

        # Elemente konfigurieren
        for i, (metric, stat) in enumerate(metric_configs):
            elements[i].metric = metric
            elements[i].stat = stat
            elements[i].deviceId = 0  # Standardgerät
            elements[i].arrayIndex = 0

        # Abfrage registrieren
        status = self.pm_dll.pmRegisterDynamicQuery(
            self.session, byref(self.query), elements, num_elements, window_size_ms, metric_offset
        )

        if status != const.PM_STATUS_SUCCESS:
            logging.error(f"pmRegisterDynamicQuery fehlgeschlagen mit Status: {status}")
            self.pm_dll.pmCloseSession(self.session)
            return False

        logging.info(f"PresentMon-Überwachung für PID {self.pid} mit {num_elements} Metriken gestartet.")
        return True

    def poll(self):
        """
        Fragt neue Frametime-Daten ab, aktualisiert die MetricData-Instanz und gibt sie zurück.

        Returns:
            MetricData: Aktuelle Metriken oder None bei Fehler
        """
        if not self.query or not self.pm_dll:
            return None

        # 19 Metriken * 8 Bytes pro double + zusätzlich Platz für Strings
        blob_size = 256  # Großzügiger Puffer für alle Daten inkl. Strings
        data_buffer = (ctypes.c_uint8 * blob_size)()
        blobs_written = c_uint32(1)

        status = self.pm_dll.pmPollDynamicQuery(self.query, self.pid, data_buffer, byref(blobs_written))

        if status == const.PM_STATUS_SUCCESS and blobs_written.value > 0:
            # Alle double-Werte (numerische Metriken) extrahieren
            # Die Reihenfolge muss mit der in start() definierten Reihenfolge übereinstimmen
            try:
                offset = 0
                # FPS Metriken (6 doubles)
                self.metrics.fps_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.fps_01 = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.fps_95 = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.fps_99 = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.fps_max = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.fps_min = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # Frametimes und Performance (4 doubles)
                # const.PM_METRIC_CPU_FRAME_TIME
                self.metrics.frame_duration_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_CPU_BUSY
                self.metrics.cpu_busy_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_CPU_WAIT
                self.metrics.frame_pacing_stall_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_GPU_TIME
                self.metrics.gpu_time_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_GPU_BUSY
                self.metrics.gpu_busy_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # Latenz (3 doubles)
                # const.PM_METRIC_DISPLAY_LATENCY
                self.metrics.display_latency_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_DISPLAYED_TIME
                self.metrics.display_duration_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_CLICK_TO_PHOTON_LATENCY
                self.metrics.input_latency_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # GPU Power (1 double)
                self.metrics.gpu_power_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # CPU-Metriken (2 doubles)
                # const.PM_METRIC_CPU_UTILIZATION
                self.metrics.cpu_utilization = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # const.PM_METRIC_CPU_FREQUENCY
                # CPU-Frequenz kommt in MHz, umrechnen in GHz und begrenzen auf sinnvolle Werte
                cpu_freq_raw = struct.unpack_from("d", data_buffer, offset)[0]
                # Überprüfen und konvertieren, falls nötig
                self.metrics.cpu_frequency = cpu_freq_raw
                offset += 8

                # CPU Frame Time für Abwärtskompatibilität (redundant, bereits in frame_duration_avg)
                self.metrics.cpu_frame_time_avg = self.metrics.cpu_busy_avg
                return self.metrics
            except Exception as e:
                logging.error(f"Fehler beim Parsen der Metrikdaten: {e}")
                return None

        elif status != const.PM_STATUS_SUCCESS:
            logging.error(f"pmPollDynamicQuery ist mit Status fehlgeschlagen: {status}")
            return None

        return None

    def stop(self):
        """
        Beendet die Überwachungssitzung und gibt Ressourcen frei.
        """
        if not self.pm_dll:
            return

        if self.query:
            self.pm_dll.pmFreeDynamicQuery(self.query)
            self.query = c_void_p()
            logging.info("PresentMon-Query freigegeben.")
        if self.session:
            self.pm_dll.pmCloseSession(self.session)
            self.session = c_void_p()
            logging.info("PresentMon-Sitzung geschlossen.")

    def get_metrics(self):
        """
        Führt eine Abfrage durch und gibt die aktuellen Metriken zurück.

        Returns:
            MetricData: Die aktuellen Performance-Metriken oder None bei Fehler
        """
        return self.poll()

    def get_api_version(self) -> Optional[Tuple[int, int, int]]:
        """
        Ruft die Version der PresentMon-API ab.

        Returns:
            Ein Tupel (major, minor, patch) oder None bei einem Fehler.
        """
        if not self.pm_dll:
            logging.error("PresentMonAPI2Loader.dll ist nicht geladen.")
            return None

        version_struct = const.PM_VERSION()
        status = self.pm_dll.pmGetApiVersion(byref(version_struct))

        if status == const.PM_STATUS_SUCCESS:
            logging.info(
                f"PresentMon API Version: "
                f"{version_struct.major}."
                f"{version_struct.minor}."
                f"{version_struct.patch}"
            )
            return version_struct.major, version_struct.minor, version_struct.patch
        else:
            logging.error(f"pmGetApiVersion fehlgeschlagen mit Status: {status}")
            return None
