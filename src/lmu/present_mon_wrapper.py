import ctypes
import logging
import struct
from ctypes import c_void_p, c_uint32, byref, c_double, c_uint64, Structure

from lmu.globals import get_present_mon_service_loader

# Metrik-Konstanten aus PresentMonAPI.h
PM_METRIC_APPLICATION = 0
PM_METRIC_CPU_FRAME_TIME = 8
PM_METRIC_CPU_WAIT = 10
PM_METRIC_DISPLAYED_FPS = 11
PM_METRIC_PRESENTED_FPS = 12
PM_METRIC_GPU_TIME = 13
PM_METRIC_GPU_BUSY = 14
PM_METRIC_DISPLAY_LATENCY = 24
PM_METRIC_CLICK_TO_PHOTON_LATENCY = 25
PM_METRIC_GPU_POWER = 27
PM_METRIC_GPU_UTILIZATION = 32
PM_METRIC_CPU_UTILIZATION = 58
PM_METRIC_CPU_FREQUENCY = 62
PM_METRIC_CPU_CORE_UTILITY = 63
PM_METRIC_DISPLAYED_TIME = 17

# Stat-Konstanten aus PresentMonAPI.h
PM_STAT_NONE = 0
PM_STAT_AVG = 1
PM_STAT_PERCENTILE_99 = 2
PM_STAT_PERCENTILE_95 = 3
PM_STAT_PERCENTILE_90 = 4
PM_STAT_MAX = 8
PM_STAT_MIN = 9
PM_STAT_MID_POINT = 10
PM_STAT_NON_ZERO_AVG = 15

# Status-Konstanten aus PresentMonAPI.h
PM_STATUS_SUCCESS = 0


class PM_QUERY_ELEMENT(Structure):
    """
    Spiegelt die PM_QUERY_ELEMENT-Struktur aus PresentMonAPI.h wider.
    """

    _fields_ = [
        ("metric", c_uint32),
        ("stat", c_uint32),
        ("deviceId", c_uint32),
        ("arrayIndex", c_uint32),
        ("dataOffset", c_uint64),
        ("dataSize", c_uint64),
    ]


class MetricData:
    """
    Speichert alle erfassten PresentMon-Metriken.
    """

    def __init__(self):
        # FPS Metriken
        self.fps_avg = 0.0
        self.fps_90 = 0.0
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
        FPS: {self.fps_avg:.2f} (90%: {self.fps_90:.2f}, 95%: {self.fps_95:.2f}, 99%: {self.fps_99:.2f})
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
            ctypes.POINTER(PM_QUERY_ELEMENT),
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

    def start(self, process_id: int, window_size_ms: float = 500.0):
        """
        Startet eine Überwachungssitzung für eine gegebene Prozess-ID.

        Args:
            process_id: Die zu überwachende Prozess-ID
            window_size_ms: Zeitfenster für die Metriken (in Millisekunden)
        """
        if not self.pm_dll:
            return

        self.pid = process_id
        status = self.pm_dll.pmOpenSession(byref(self.session))
        if status != PM_STATUS_SUCCESS:
            logging.error(f"pmOpenSession fehlgeschlagen mit Status: {status}")
            return

        status = self.pm_dll.pmStartTrackingProcess(self.session, self.pid)
        if status != PM_STATUS_SUCCESS:
            logging.error(f"pmStartTrackingProcess fehlgeschlagen mit Status: {status}")
            self.pm_dll.pmCloseSession(self.session)
            return

        # Erstellen einer Liste von Query-Elementen für alle gewünschten Metriken
        metric_configs = [
            # FPS Metriken
            (PM_METRIC_PRESENTED_FPS, PM_STAT_AVG),  # fps_avg
            (PM_METRIC_PRESENTED_FPS, PM_STAT_PERCENTILE_90),  # fps_90
            (PM_METRIC_PRESENTED_FPS, PM_STAT_PERCENTILE_95),  # fps_95
            (PM_METRIC_PRESENTED_FPS, PM_STAT_PERCENTILE_99),  # fps_99
            (PM_METRIC_PRESENTED_FPS, PM_STAT_MAX),  # fps_max
            (PM_METRIC_PRESENTED_FPS, PM_STAT_MIN),  # fps_min
            # Frametimes und Performance
            (PM_METRIC_CPU_FRAME_TIME, PM_STAT_AVG),  # frame_duration_avg
            (PM_METRIC_CPU_WAIT, PM_STAT_AVG),  # frame_pacing_stall_avg
            (PM_METRIC_GPU_TIME, PM_STAT_AVG),  # gpu_time_avg
            (PM_METRIC_GPU_BUSY, PM_STAT_AVG),  # gpu_busy_avg
            # Latenz
            (PM_METRIC_DISPLAY_LATENCY, PM_STAT_AVG),  # display_latency_avg
            (PM_METRIC_DISPLAYED_TIME, PM_STAT_AVG),  # display_duration_avg
            (PM_METRIC_CLICK_TO_PHOTON_LATENCY, PM_STAT_NON_ZERO_AVG),  # input_latency_avg
            # Hardware-Metriken
            (PM_METRIC_GPU_POWER, PM_STAT_AVG),  # gpu_power_avg
            # CPU-Metriken
            (PM_METRIC_CPU_UTILIZATION, PM_STAT_AVG),  # cpu_utilization
            (PM_METRIC_CPU_FREQUENCY, PM_STAT_AVG),  # cpu_frequency
        ]

        num_elements = len(metric_configs)
        elements = (PM_QUERY_ELEMENT * num_elements)()

        # Elemente konfigurieren
        for i, (metric, stat) in enumerate(metric_configs):
            elements[i].metric = metric
            elements[i].stat = stat
            elements[i].deviceId = 0  # Standardgerät
            elements[i].arrayIndex = 0

        # Abfrage registrieren
        status = self.pm_dll.pmRegisterDynamicQuery(
            self.session,
            byref(self.query),
            elements,
            num_elements,
            window_size_ms,  # Zeitfenster in ms
            0.0,  # Kein Offset
        )

        if status != PM_STATUS_SUCCESS:
            logging.error(f"pmRegisterDynamicQuery fehlgeschlagen mit Status: {status}")
            self.pm_dll.pmCloseSession(self.session)
            return

        logging.info(f"PresentMon-Überwachung für PID {self.pid} mit {num_elements} Metriken gestartet.")

    def poll(self):
        """
        Fragt neue Frametime-Daten ab, aktualisiert die MetricData-Instanz und gibt sie zurück.

        Returns:
            MetricData: Aktuelle Metriken oder None bei Fehler
        """
        if not self.query or not self.pm_dll:
            return None

        # 19 Metriken * 8 Bytes pro double + zusätzlich Platz für Strings
        blob_size = 1024  # Großzügiger Puffer für alle Daten inkl. Strings
        data_buffer = (ctypes.c_uint8 * blob_size)()
        blobs_written = c_uint32(1)

        status = self.pm_dll.pmPollDynamicQuery(self.query, self.pid, data_buffer, byref(blobs_written))

        if status == PM_STATUS_SUCCESS and blobs_written.value > 0:
            # Alle double-Werte (numerische Metriken) extrahieren
            # Die Reihenfolge muss mit der in start() definierten Reihenfolge übereinstimmen
            try:
                offset = 0
                # FPS Metriken (6 doubles)
                self.metrics.fps_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.fps_90 = struct.unpack_from("d", data_buffer, offset)[0]
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
                self.metrics.frame_duration_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.frame_pacing_stall_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.gpu_time_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.gpu_busy_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # Latenz (3 doubles)
                self.metrics.display_latency_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.display_duration_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                self.metrics.input_latency_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # GPU Power (1 double)
                self.metrics.gpu_power_avg = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8

                # CPU-Metriken (3 doubles)
                self.metrics.cpu_utilization = struct.unpack_from("d", data_buffer, offset)[0]
                offset += 8
                # CPU-Frequenz kommt in MHz, umrechnen in GHz und begrenzen auf sinnvolle Werte
                cpu_freq_raw = struct.unpack_from("d", data_buffer, offset)[0]
                # Überprüfen und konvertieren, falls nötig
                if cpu_freq_raw > 10000:  # Wenn Wert in Hz statt MHz
                    self.metrics.cpu_frequency = cpu_freq_raw / 1000000.0  # Hz zu GHz
                elif cpu_freq_raw > 100:  # Wenn Wert in MHz
                    self.metrics.cpu_frequency = cpu_freq_raw / 1000.0  # MHz zu GHz
                else:  # Bereits in GHz oder bereits korrigiert
                    self.metrics.cpu_frequency = cpu_freq_raw
                # Plausibilitätsprüfung
                if self.metrics.cpu_frequency > 6.0:  # Heutiger max. realistischer Wert
                    self.metrics.cpu_frequency = 0.0  # Ungültiger Wert, auf 0 setzen
                offset += 8

                # CPU Frame Time für Abwärtskompatibilität (redundant, bereits in frame_duration_avg)
                self.metrics.cpu_frame_time_avg = self.metrics.frame_duration_avg

                # Detailliertes Debug-Log bei Bedarf
                # logging.info(str(self.metrics))
                return self.metrics

            except Exception as e:
                logging.error(f"Fehler beim Parsen der Metrikdaten: {e}")
                return None

        elif status != PM_STATUS_SUCCESS:
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
