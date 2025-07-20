<template>
  <div class="performance-info-container">
    <!-- Haupt-Metriken im Fokus -->
    <div class="main-metrics-section">
      <div class="metrics-container">
        <div class="metric-box cpu-metric">
          <div class="metric-title">CPU</div>
          <div class="metric-value">{{ performanceData.cpu_frame_time_avg.toFixed(2) }} ms</div>
        </div>
        <div class="metric-box gpu-metric">
          <div class="metric-title">GPU</div>
          <div class="metric-value">{{ performanceData.gpu_time_avg.toFixed(2) }} ms</div>
        </div>
      </div>

      <!-- Performance Graph -->
      <div class="performance-graph-container">
        <canvas ref="performanceChart"></canvas>
      </div>
    </div>

    <!-- Detaillierte Metriken -->
    <div class="detailed-metrics-section">
      <div class="metrics-grid">
        <!-- FPS Metriken -->
        <div class="metric-group">
          <h4>FPS</h4>
          <div class="metric-row">
            <span class="metric-label">Average:</span>
            <span class="metric-value">{{ performanceData.fps_avg.toFixed(1) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">90. Percentil:</span>
            <span class="metric-value">{{ performanceData.fps_90.toFixed(1) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">95. Percentil:</span>
            <span class="metric-value">{{ performanceData.fps_95.toFixed(1) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">99. Percentil:</span>
            <span class="metric-value">{{ performanceData.fps_99.toFixed(1) }}</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Min/Max:</span>
            <span class="metric-value">{{ performanceData.fps_min.toFixed(1) }} / {{ performanceData.fps_max.toFixed(1) }}</span>
          </div>
        </div>

        <!-- Frametime & Performance -->
        <div class="metric-group">
          <h4>Frame Performance</h4>
          <div class="metric-row">
            <span class="metric-label">Frame Zeit:</span>
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
        <div class="metric-group d-none">
          <h4>Latenz</h4>
          <div class="metric-row">
            <span class="metric-label">Display:</span>
            <span class="metric-value">{{ performanceData.display_latency_avg.toFixed(2) }} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Display Dauer:</span>
            <span class="metric-value">{{ performanceData.display_duration_avg.toFixed(2) }} ms</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">Input:</span>
            <span class="metric-value">{{ performanceData.input_latency_avg.toFixed(2) }} ms</span>
          </div>
        </div>

        <!-- Hardware -->
        <div class="metric-group d-none">
          <h4>Hardware</h4>
          <div class="metric-row">
            <span class="metric-label">GPU Leistung:</span>
            <span class="metric-value">{{ performanceData.gpu_power_avg.toFixed(1) }}W</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">CPU Auslastung:</span>
            <span class="metric-value">{{ performanceData.cpu_utilization.toFixed(1) }}%</span>
          </div>
          <div class="metric-row">
            <span class="metric-label">CPU Frequenz:</span>
            <span class="metric-value">{{ formatCpuFrequency() }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';
import 'chartjs-plugin-zoom';

export default {
  name: 'PerformanceInfo',
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
      chart: null,
      cpuTimes: Array(60).fill(0),
      gpuTimes: Array(60).fill(0),
      timeLabels: Array(60).fill('')
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
    if (this.chart) {
      this.chart.destroy();
    }
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
  },
  methods: {
    initChart() {
      const ctx = this.$refs.performanceChart.getContext('2d');

      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.timeLabels,
          datasets: [
            {
              label: 'CPU (ms)',
              data: this.cpuTimes,
              borderColor: '#728bb0', // Hellblau für CPU
              backgroundColor: 'rgba(114, 139, 176, 0.2)',
              borderWidth: 2,
              tension: 0.3,
              pointRadius: 0
            },
            {
              label: 'GPU (ms)',
              data: this.gpuTimes,
              borderColor: '#f86045', // Orange für GPU
              backgroundColor: 'rgba(248, 96, 69, 0.2)',
              borderWidth: 2,
              tension: 0.3,
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 0 // Deaktiviere Animationen für bessere Performance
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Time'
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
              enabled: false,
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          }
        }
      });
    },
    updateChartData() {
      // Werte aus den props übernehmen
      const cpuTime = this.performanceData.cpu_frame_time_avg;
      const gpuTime = this.performanceData.gpu_time_avg;

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

      // Chart aktualisieren
      this.chart.update('none'); // 'none' für beste Performance
    },
    formatCpuFrequency() {
      if (this.performanceData.cpu_frequency <= 0.0) {
        return "Nicht verfügbar";
      }
      return `${this.performanceData.cpu_frequency.toFixed(2)} GHz`;
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

<style scoped>
.performance-info-container {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
}

.main-metrics-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metrics-container {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 0.5rem;
}

.metric-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 1rem;
  border-radius: 8px;
  min-width: 140px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: relative;
}

.cpu-metric {
  background-color: rgba(114, 139, 176, 0.2);
  border: 1px solid #728bb0;
}

.gpu-metric {
  background-color: rgba(248, 96, 69, 0.2);
  border: 1px solid #f86045;
}

.metric-title {
  position: absolute;
  top: 0.25rem;
  left: 0.15rem;
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.3rem;
  text-orientation: mixed;
  writing-mode: vertical-lr;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  align-self: end;
}

.performance-graph-container {
  height: 150px;
  width: 100%;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.detailed-metrics-section {
  background-color: rgba(0, 0, 0, 0.05);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.metric-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric-group h4 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: #ccc;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.3rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.metric-label {
  color: #aaa;
}

.detailed-metrics-section .metric-value {
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .metrics-container {
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }

  .metric-box {
    width: 100%;
    max-width: 300px;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
