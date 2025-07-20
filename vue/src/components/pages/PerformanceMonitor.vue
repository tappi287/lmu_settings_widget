<template>
  <PerformanceInfo :performanceData="performanceData" />
</template>

<script>
import PerformanceInfo from '../widgets/PerformanceInfo.vue';

export default {
  name: 'PerformanceMonitor',
  components: {
    PerformanceInfo
  },
  data() {
    return {
      performanceData: {
        // FPS Metriken
        fps_avg: 0.0,
        fps_90: 0.0,
        fps_95: 0.0,
        fps_99: 0.0,
        fps_max: 0.0,
        fps_min: 0.0,

        // Frametimes und Performance
        frame_duration_avg: 0.0,
        frame_pacing_stall_avg: 0.0,
        gpu_time_avg: 0.0,
        gpu_busy_avg: 0.0,
        cpu_frame_time_avg: 0.0,

        // Latenz
        display_latency_avg: 0.0,
        display_duration_avg: 0.0,
        input_latency_avg: 0.0,

        // Hardware-Metriken
        gpu_power_avg: 0.0,

        // CPU-Metriken
        cpu_utilization: 0.0,
        cpu_frequency: 0.0
      },
      updateInterval: null
    };
  },
  mounted() {
    // Verbindung zum Backend herstellen und Performance-Monitoring starten
    this.startPerformanceMonitor();
  },
  beforeDestroy() {
    // Timer stoppen
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }

    // Performance-Monitor stoppen
    window.eel.stop_performance_monitor()((success) => {
      if (success) {
        console.log('Performance-Monitor erfolgreich gestoppt');
      } else {
        console.error('Fehler beim Stoppen des Performance-Monitors');
      }
    });
  },
  methods: {
    // Daten vom Backend abrufen
    fetchPerformanceData() {
      window.eel.get_performance_metrics()((data) => {
        try {
          const parsedData = JSON.parse(data);
          if (Object.keys(parsedData).length > 0) {
            this.performanceData = parsedData;
          }
        } catch (error) {
          console.error('Fehler beim Parsen der Performance-Daten:', error);
        }
      });
    },

    // Performance-Monitor starten
    startPerformanceMonitor() {
      // Zuerst den Monitor initialisieren (PID = null für automatische Erkennung)
      window.eel.init_performance_monitor(null)((success) => {
        if (success) {
          console.log('Performance-Monitor erfolgreich initialisiert');
          // Regelmäßiges Abrufen der Daten starten
          this.updateInterval = setInterval(() => {
            this.fetchPerformanceData();
          }, 1000);
        } else {
          console.error('Fehler bei der Initialisierung des Performance-Monitors');
          // Fallback auf Simulation für Tests oder Entwicklung
          this.startDataSimulation();
        }
      });
    },

    // Für Entwicklungs- und Testzwecke
    startDataSimulation() {
      console.log('Verwende simulierte Performance-Daten');
      this.updateInterval = setInterval(() => {
        // Simulierte Daten
        this.performanceData = {
          fps_avg: 60 + (Math.random() * 20 - 10),
          fps_90: 55 + (Math.random() * 10 - 5),
          fps_95: 50 + (Math.random() * 10 - 5),
          fps_99: 45 + (Math.random() * 10 - 5),
          fps_max: 75 + (Math.random() * 10),
          fps_min: 40 + (Math.random() * 10 - 5),

          frame_duration_avg: 16.67 + (Math.random() * 2 - 1),
          frame_pacing_stall_avg: 0.5 + (Math.random() * 1),
          gpu_time_avg: 8 + (Math.random() * 10 - 2),
          gpu_busy_avg: 70 + (Math.random() * 20 - 10),
          cpu_frame_time_avg: 5 + (Math.random() * 4 - 1.5),

          display_latency_avg: 10 + (Math.random() * 5 - 2.5),
          display_duration_avg: 8.3 + (Math.random() * 1),
          input_latency_avg: 20 + (Math.random() * 8 - 4),

          gpu_power_avg: 150 + (Math.random() * 30 - 15),

          cpu_utilization: 15 + (Math.random() * 10 - 5),
          cpu_frequency: 4.8 + (Math.random() * 0.4 - 0.2)
        };
      }, 1000);
    }
  }
};
</script>

<style scoped>
.performance-monitor-page {
  padding: 1.5rem;
  height: 100%;
  overflow-y: auto;
}

.page-title {
  margin-bottom: 1.5rem;
  font-size: 1.75rem;
  color: #eee;
}

.performance-container {
  background-color: #2d2d2d;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}
</style>
