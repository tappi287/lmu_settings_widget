<template>
  <div class="hardware-info-container text-left">
    <!-- CPU Utilization -->
    <div class="system-info-section">
      <div class="info-label">CPU Utilization</div>
      <div class="cpu-grid">
        <div v-for="(usage, index) in filteredCpuUtilization" :key="'cpu-' + index" class="cpu-core">
          <div class="core-label">{{ cpuOriginalIndices[index] }}</div>
          <div class="core-bar-container">
            <div class="core-bar" :style="getCpuBarStyle(usage)"></div>
          </div>
          <div class="core-value">{{ Math.round(usage) }}%</div>
        </div>
      </div>
    </div>

    <!-- RAM Information -->
    <div class="system-info-section">
      <div class="info-label">RAM: {{ formatMemory(hardwareInfo.ram_used) }} / {{ formatMemory(hardwareInfo.ram_total) }} ({{ Math.round(hardwareInfo.ram_used_percent) }}%)</div>
      <b-progress height="20px" class="mb-3">
        <b-progress-bar :variant="getMemoryVariant(hardwareInfo.ram_used_percent)" :value="hardwareInfo.ram_used_percent" :max="100" />
      </b-progress>
    </div>

    <!-- GPU Information (for each GPU) -->
    <div v-for="(gpu, index) in hardwareInfo.gpus" :key="'gpu-' + index" class="system-info-section">
      <div class="info-label">
        GPU {{ index + 1 }}: {{ formatMemory(gpu.vram_used) }} / {{ formatMemory(gpu.vram_total) }} 
        ({{ Math.round(gpu.vram_used_percent) }}%)
      </div>
      <b-progress height="20px" class="mb-3">
        <b-progress-bar :variant="getMemoryVariant(gpu.vram_used_percent)" :value="gpu.vram_used_percent" :max="100" />
      </b-progress>

      <div class="info-label">
        GPU Temp: {{ gpu.gpu_temperature }}°C | GPU Load: {{ gpu.gpu_utilization }}%
      </div>
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
    filteredCpuUtilization() {
      // Filtere CPU-Kerne mit Auslastung < 0.25 heraus, behalte aber die Indizes bei
      const activeCores = [];
      this.cpuOriginalIndices = [];

      this.hardwareInfo.cpu_utilization.forEach((usage, index) => {
        if (usage >= 0.25) {
          activeCores.push(usage);
          this.cpuOriginalIndices.push(index);
        }
      });

      // Wenn keine aktiven Kerne gefunden wurden, zeige die 4 mit der höchsten Auslastung
      if (activeCores.length === 0) {
        const sortedIndices = [...this.hardwareInfo.cpu_utilization.keys()]
          .sort((a, b) => this.hardwareInfo.cpu_utilization[b] - this.hardwareInfo.cpu_utilization[a])
          .slice(0, 4);

        sortedIndices.sort((a, b) => a - b); // Sortiere nach Kern-Nummer

        sortedIndices.forEach(index => {
          activeCores.push(this.hardwareInfo.cpu_utilization[index]);
          this.cpuOriginalIndices.push(index);
        });
      }

      return activeCores;
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
      if (percentage < 50) return 'success';
      if (percentage < 80) return 'warning';
      return 'danger';
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
</style>
