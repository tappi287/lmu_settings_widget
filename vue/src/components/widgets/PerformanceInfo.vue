<template>
  <div class="performance-info-container">
    <!-- Haupt-Metriken im Fokus -->
    <div class="main-metrics-section">
      <div class="metrics-container">
        <div class="metric-row cpu-metric">
          <div class="metric-title">Overall</div>
          <div class="metric-value">{{ performanceData.cpu_frame_time_avg.toFixed(2) }} ms</div>
        </div>
        <div class="metric-row gpu-metric">
          <div class="metric-title">GPU</div>
          <div class="metric-value">{{ performanceData.gpu_busy_avg.toFixed(2) }} ms</div>
        </div>
      </div>

      <!-- Performance Graphs -->
      <div class="performance-graphs-container">
        <div class="chart-container">
          <canvas ref="cpuPerformanceChart"></canvas>
        </div>
        <div class="chart-container">
          <canvas ref="gpuPerformanceChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Detaillierte Metriken -->
    <div class="detailed-metrics-section">
      <div class="metrics-grid">
        <!-- FPS Metriken -->
        <div class="metric-group">
          <div class="metric-row">
            <span class="metric-label">FPS Average:</span>
            <span class="metric-value">{{ performanceData.fps_avg.toFixed(1) }}</span>
          </div>
          <div class="metric-row d-none metric-row">
            <span class="metric-label">FPS 90. Percentil:</span>
            <span class="metric-value">{{ performanceData.fps_90.toFixed(1) }}</span>
          </div>
          <div class="metric-row d-none">
            <span class="metric-label">FPS 95. Percentil:</span>
            <span class="metric-value">{{ performanceData.fps_95.toFixed(1) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">FPS 99. Percentil:</span>
            <span class="metric-value">{{ performanceData.fps_99.toFixed(1) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">FPS Min/Max:</span>
            <span class="metric-value">{{ performanceData.fps_min.toFixed(1) }} / {{ performanceData.fps_max.toFixed(1) }}</span>
          </div>
        </div>

        <!-- Frametime & Performance -->
        <div class="metric-group">
          <div class="metric-row">
            <span class="metric-label">FrameTime:</span>
            <span class="metric-value">{{ performanceData.frame_duration_avg.toFixed(2) }} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Stall:</span>
            <span class="metric-value">{{ performanceData.frame_pacing_stall_avg.toFixed(2) }} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">GPU Busy:</span>
            <span class="metric-value">{{ performanceData.gpu_busy_avg.toFixed(1) }}%</span>
          </div>
        </div>

        <!-- Latenz -->
        <div class="metric-group">
          <div class="metric-row">
            <span class="metric-label">Display Latency:</span>
            <span class="metric-value">{{ performanceData.display_latency_avg.toFixed(2) }} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Display Duration:</span>
            <span class="metric-value">{{ performanceData.display_duration_avg.toFixed(2) }} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Input Latency:</span>
            <span class="metric-value">{{ performanceData.input_latency_avg.toFixed(2) }} ms</span>
          </div>
        </div>

        <!-- Hardware -->
        <div class="metric-group">
          <div class="metric-row">
            <span class="metric-label">GPU Power:</span>
            <span class="metric-value">{{ performanceData.gpu_power_avg.toFixed(1) }}W</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">CPU Load:</span>
            <span class="metric-value">{{ performanceData.cpu_utilization.toFixed(1) }}%</span>
          </div>
          <div class="metric-row d-none">
            <span class="metric-label">CPU Frequency:</span>
            <span class="metric-value">{{ formatCpuFrequency() }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="metric-settings-section">
      <div class="metrics-container">
        <div class="metric-row metric-setting">
          <SettingItem class="w-100" :setting="targetFpsSetting" @setting-changed="updateTargetFps" variant="rf-secondary"></SettingItem>
        </div>
        <div class="metric-row metric-setting d-none">
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import 'chartjs-plugin-zoom';
import SettingItem from "@/components/settings/SettingItem.vue";

export default {
  name: 'PerformanceInfo',
  components: {SettingItem},
  props: {
    performanceData: {
      type: Object,
      default: () => ({
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
      })
    }
  },
  data() {
    return {
      cpuChart: null,
      gpuChart: null,
      cpuTimes: Array(60).fill(0),
      gpuTimes: Array(60).fill(0),
      timeLabels: Array(60).fill(''),
      targetFps: 90,
      targetFrameTime: 11.11,
      targetFpsSetting: {
        name: "Target FPS",
        key: "targetFps",
        desc: "Frame times below this value will appear orange",
        value: 90,
        settings: [
            {value: 72, name: "72 Hz"},
            {value: 90, name: "90 Hz"},
            {value: 120, name: "120 Hz"},
            {value: 144, name: "144 Hz"}
        ]
    },
    };
  },
  mounted() {
    this.initChart();
    // Initialisieren der Zeitlabels (leere Strings für den Anfang)
    this.timeLabels = Array(60).fill('');

    // Timer für regelmäßiges Update der Chartdaten
    this.updateTimer = setInterval(() => {
      this.updateChartData();
    }, 1000); // Alle Sekunde aktualisieren
  },
  beforeDestroy() {
    if (this.cpuChart) {
      this.cpuChart.destroy();
    }
    if (this.gpuChart) {
      this.gpuChart.destroy();
    }
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
  },
  methods: {
    destroyCharts() {
      if (this.cpuChart) {this.cpuChart.destroy();}
      if (this.gpuChart) {this.gpuChart.destroy();}
    },
    initChart() {
      const cpuCtx = this.$refs.cpuPerformanceChart.getContext('2d');
      const gpuCtx = this.$refs.gpuPerformanceChart.getContext('2d');

      // Gemeinsame Chart-Optionen
      const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 0 // Deaktiviere Animationen für bessere Performance
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: false
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          },
          x: {
            display: false, // x-Achse ausblenden für aufgeräumteres Design
            grid: {
              display: false
            }
          }
        },
        plugins: {
          zoom: {
            zoom: {
              wheel: {
                enabled: true
              },
              pinch: {
                enabled: true
              },
              mode: 'y'
            },
            pan: {
              enabled: true,
              mode: 'y'
            }
          },
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false
          },
          title: {
            display: false,
            align: 'center',
            text: "Title",
          }
        },
        barPercentage: 1.0,
        categoryPercentage: 1.0,
        borderSkipped: false
      };

      // CPU Chart
      this.cpuChart = new Chart(cpuCtx, {
        type: 'bar',
        data: {
          labels: this.timeLabels,
          datasets: [{
            label: 'CPU (ms)',
            data: this.cpuTimes,
            backgroundColor: (context) => {
              const value = context.dataset.data[context.dataIndex];
              return value <= this.targetFrameTime ? '#4CAF50' : '#FF9800'; // Grün wenn <= 11.1ms (90Hz), sonst Orange
            },
            borderWidth: 0
          }]
        },
        options: commonOptions
      });

      // GPU Chart
      this.gpuChart = new Chart(gpuCtx, {
        type: 'bar',
        data: {
          labels: this.timeLabels,
          datasets: [{
            label: 'GPU (ms)',
            data: this.gpuTimes,
            backgroundColor: (context) => {
              const value = context.dataset.data[context.dataIndex];
              return value <= this.targetFrameTime ? '#4CAF50' : '#FF9800'; // Grün wenn <= 11.1ms (90Hz), sonst Orange
            },
            borderWidth: 0
          }]
        },
        options: commonOptions
      });
    },
    updateChartData() {
      // Werte aus den props übernehmen
      const cpuTime = this.performanceData.cpu_frame_time_avg;
      const gpuTime = this.performanceData.gpu_busy_avg;

      // Aktuelles Datum und Uhrzeit für das Label
      const now = new Date();
      const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

      // Array verschieben und neuen Wert anfügen
      this.cpuTimes.shift();
      this.cpuTimes.push(cpuTime);

      this.gpuTimes.shift();
      this.gpuTimes.push(gpuTime);

      this.timeLabels.shift();
      this.timeLabels.push(timeString);

      // Charts aktualisieren
      this.cpuChart.update('none'); // 'none' für beste Performance
      this.gpuChart.update('none');
    },
    formatCpuFrequency() {
      if (this.performanceData.cpu_frequency <= 0.0) {
        return "Nicht verfügbar";
      }
      return `${this.performanceData.cpu_frequency.toFixed(2)} GHz`;
    },
    updateTargetFps(setting, value) {
      this.targetFrameTime = Number(Number(1000 / value).toFixed(2))
      this.targetFps = value
      console.log(`Set target fps: ${value} Frame time: ${this.targetFrameTime}`);
      this.destroyCharts()
      this.initChart()
    }
  },
  watch: {
    performanceData: {
      deep: true,
      handler() {
        // Wenn sich die Daten ändern, Chart aktualisieren
        this.updateChartData();
      }
    }
  }
};
</script>

<style src="../../assets/perf_info.css">
</style>
