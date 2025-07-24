<template>
  <div class="hardware-info-container text-left">
    <!-- CPU Utilization -->
    <div class="system-info-section d-none">
      <div class="info-label">CPU Utilization</div>
      
      <!-- Top 8 CPU Cores -->
      <div class="cpu-grid">
        <div v-for="(usage, index) in topCpuCores" :key="'cpu-' + index" class="cpu-core">
          <div class="core-label">CPU {{ cpuOriginalIndices[index] }}</div>
          <div class="core-bar-container">
            <div class="core-bar" :style="getCpuBarStyle(usage)"></div>
          </div>
          <div class="core-value">{{ Math.round(usage) }}%</div>
        </div>
      </div>
    </div>

    <!-- RAM Information -->
    <div class="system-info-section">
      <div class="info-label">
        RAM: <div class="float-right">{{ formatMemory(hardwareInfo.ram_used) }} / {{ formatMemory(hardwareInfo.ram_total) }} ({{ Math.round(hardwareInfo.ram_used_percent) }}%)</div>
      </div>
      <b-progress height="20px" class="mb-3 rounded">
        <b-progress-bar class="hw-bar" :value="hardwareInfo.ram_used_percent" :max="100">
          {{ Math.round(hardwareInfo.ram_used_percent) }}%
        </b-progress-bar>
      </b-progress>
    </div>

    <!-- GPU Information (for each GPU) -->
    <div v-for="(gpu, index) in hardwareInfo.gpus" :key="'gpu-' + index" class="system-info-section">
      <div class="info-label">
        GPU {{ index + 1 }} vRAM <div class="float-right">{{ formatMemory(gpu.vram_used) }} / {{ formatMemory(gpu.vram_total) }} ({{ Math.round(gpu.vram_used_percent) }}%)</div>
      </div>
      <b-progress height="20px" class="mb-3 rounded">
        <b-progress-bar class="hw-bar" :value="gpu.vram_used_percent" :max="100">
          {{ Math.round(gpu.vram_used_percent) }}%
        </b-progress-bar>
      </b-progress>

      <div class="info-label">
        GPU {{ index + 1 }} Load <div class="float-right">{{ gpu.gpu_utilization }}%</div>
      </div>
      <b-progress height="20px" class="mb-3 rounded">
        <b-progress-bar class="hw-bar" :value="gpu.gpu_utilization" :max="100">
          {{ gpu.gpu_utilization }}%
        </b-progress-bar>
      </b-progress>
      <div class="info-label">
        GPU Temperature<div class="float-right">{{ gpu.gpu_temperature }}°C</div>
      </div>
      <b-progress height="20px" class="mb-3 rounded">
        <b-progress-bar class="hw-bar" :value="gpu.gpu_temperature" :max="100">
          {{ gpu.gpu_temperature }}°C
        </b-progress-bar>
      </b-progress>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HardwareInfo',
  props: {
    hardwareInfo: {
      type: Object,
      default: () => ({
        cpu_utilization: Array(28).fill(0),
        device_type: 'cuda',
        gpus: [{
          gpu_temperature: 0,
          gpu_utilization: 0,
          vram_total: 0,
          vram_used: 0,
          vram_used_percent: 0
        }],
        ram_total: 0,
        ram_used: 0,
        ram_used_percent: 0
      })
    }
  },
  computed: {
    topCpuCores() {
      this.cpuOriginalIndices = [];
      
      // Erstelle ein Array mit Paaren [index, usage]
      const cpuPairs = this.hardwareInfo.cpu_utilization.map((usage, index) => [index, usage]);
      
      // Sortiere nach Auslastung (absteigend)
      cpuPairs.sort((a, b) => b[1] - a[1]);
      
      // Nehme die Top 8 oder weniger, wenn nicht genug vorhanden
      const topCount = Math.min(8, cpuPairs.length);
      const topPairs = cpuPairs.slice(0, topCount);
      
      // Speichere die ursprünglichen Indizes und gib die Nutzungswerte zurück
      const usageValues = [];
      topPairs.forEach(pair => {
        this.cpuOriginalIndices.push(pair[0]);
        usageValues.push(pair[1]);
      });
      
      return usageValues;
    }
  },
  data() {
    return {
      cpuOriginalIndices: []
    };
  },
  methods: {
    formatMemory(bytes) {
      return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB';
    },
    getMemoryVariant(percentage) {
      if (percentage < 50) return 'secondary';
      if (percentage < 80) return 'success';
      return 'danger';
    },
    getGpuTemperatureStyle(temp) {
      let color;
      if (temp > 90) { color = '#4e835c'; }
      if (temp < 90) { color = '#5c8868'; }
      if (temp < 70) { color = '#6a8771'; }
      if (temp < 60) { color = '#768c7c'; }
      if (temp < 50) { color = '#57675b'; }
      if (temp < 40) { color = '#606a62'; }
      if (temp < 30) { color = '#565c58'; }
      return {
        'background-color': color
      };
    },
    getCpuBarStyle(usage) {
      // Farbwerte basierend auf den Anforderungen
      let color;
      if (usage <= 50) {
        color = '#728bb0'; // Hellblau für niedrige Auslastung
      } else if (usage <= 80) {
        color = '#f86045'; // Orange für mittlere Auslastung
      } else {
        color = '#f13210'; // Rot für hohe Auslastung
      }

      return {
        'height': `${usage}%`,
        'background-color': color
      };
    }
  }
};
</script>

<style scoped>
.system-info-section {
  margin-bottom: 15px;
}

.info-label {
  margin-bottom: 5px;
  font-size: 0.9rem;
}

.overall-cpu-section {
  margin-bottom: 10px;
}

.cpu-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
  gap: 5px;
  max-height: 160px;
  overflow: hidden;
}

.cpu-core {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 80px;
}

.core-label {
  font-size: 0.7rem;
  color: #ccc;
}

.core-bar-container {
  width: 100%;
  height: 80%;
  background-color: #2c2c2c;
  border-radius: 3px;
  position: relative;
}

.core-bar {
  position: absolute;
  bottom: 0;
  width: 100%;
  border-radius: 2px;
  transition: height 0.6s ease, background-color 0.6s ease;
}

.core-value {
  font-size: 0.7rem;
  color: #ccc;
  margin-top: 2px;
}

.progress {
  background: rgba(174, 193, 211, 0.2);
}

.hw-bar {
  background-color: #4bae4f;
}
</style>