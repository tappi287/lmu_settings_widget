<template>
  <div>
    <PerformanceInfo
        :class="presentMonAvailable ? '': 'knee-board-content-fade'"
        :performanceData="performanceData" :descriptions="performanceDataDescriptions"
    />

    <!-- Enable Metrics Overlay -->
    <b-overlay no-wrap :show="!presentMonAvailable" variant="transparent">
      <template v-slot:overlay>
        <b-card class="rounded" header-class="m-0 p-2" bg-variant="dark" text-variant="white">
          <template #header>
            <h5 class="mb-0">PresentMon Service is not available</h5>
          </template>
          <b-card-text class="text-white-50">
            Performance metrics can not be captured. Look at the Help page on how to install PresentMon Service.<br />
            <b-link @click="$emit('show-help')">Show Help...</b-link>
          </b-card-text>
        </b-card>
      </template>
    </b-overlay>
  </div>
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
      performanceDataDescriptions: {
        display_latency_avg: "How long it took from the start of this frame until the frame was displayed on the screen.",
        fps_avg: "The rate at which the application is calling Present().",
        fps_99: "99th Percentile: Value below which 99% of the observations within 1s window fall.",
        fps_01: "1st Percentile: Value below which 1% of the observations within 1s window fall.",
        frame_pacing_stall_avg: "How long the CPU spent waiting before starting the next frame.",
        display_duration_avg: "How long the frame was displayed on the screen, or 'NA' if the frame was not displayed.",
        input_latency_avg: "How long it took from the earliest mouse click that contributed to this frame until this frame was displayed.",
        cpu_utilization: "Amount of CPU processing capacity being used.",
        cpu_frequency: "Clock speed of the CPU.",
        gpu_power_avg: "Power consumed by the graphics processing unit.",
        gpu_busy_avg: "How long the GPU was actively working on this frame (i.e., the time during which at least one GPU engine is executing work from the target process).",
      },
      performanceData: {
        // FPS Metriken
        fps_avg: 0.0,
        fps_01: 0.0,
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
      updateInterval: null,
      presentMonAvailable: false,
      presentMonAPIServiceVersion: ''
    };
  },
  mounted() {
    // Check if PresentMon is available
    this.getPresentMonAPIServiceVersion()
    // Verbindung zum Backend herstellen und Performance-Monitoring starten
    this.updateInterval = setInterval(() => {
      this.fetchPerformanceData();
    }, 1000);
  },
  beforeDestroy() {
    // Timer stoppen
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
  },
  methods: {
    // Get PresentMonService API version
    getPresentMonAPIServiceVersion() {
      this.presentMonAvailable = false;
      window.eel.get_present_mon_api_version()((data) => {
        try {
          const r = JSON.parse(data);
          if (r.result !== undefined && r.result) {
            this.presentMonAvailable = true;
            this.presentMonAPIServiceVersion = r.data
          }
        } catch (error) {
          console.error('Fehler beim Parsen der Performance-Daten:', error);
        }
      });
    },
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
    // Für Entwicklungs- und Testzwecke
    startDataSimulation() {
      console.log('Verwende simulierte Performance-Daten');
      this.updateInterval = setInterval(() => {
        // Simulierte Daten
        this.performanceData = {
          fps_avg: 60 + (Math.random() * 20 - 10),
          fps_01: 20 + (Math.random() * 10 - 5),
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
