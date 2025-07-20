<template>
  <div class="knee-board-container">
    <b-input-group size="sm">
      <b-input-group-prepend>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          KneeBoard
        </b-input-group-text>
      </b-input-group-prepend>
    </b-input-group>
    <div class="knee-board-content">
      <div class="info-panel">
        <b-card class="mt-2 setting-card" header-class="m-0 p-2 text-left"
                bg-variant="dark" text-variant="white">
          <template #header>
            <b-icon icon="tv"></b-icon>
            <span class="ml-2">Race Info</span>
            <slot name="header"></slot>
          </template>
          <b-row>
            <b-col>
              <p><strong>Strecke:</strong> {{ trackName }}</p>
              <p><strong>Runden:</strong> {{ currentLap }} / {{ totalLaps }}</p>
            </b-col>
            <b-col>
              <p><strong>Position:</strong> {{ position }}</p>
              <p><strong>Beste Rundenzeit:</strong> {{ bestLapTime }}</p>
            </b-col>
          </b-row>
        </b-card>
      </div>

      <div class="notes-panel h-panel-half d-none">
        <b-card class="mt-2 setting-card panel-card" header-class="m-0 p-2 text-left"
                bg-variant="dark" text-variant="white">
          <template #header>
            <b-icon icon="display"></b-icon>
            <span class="ml-2">FPS Info</span>
            <slot name="header"></slot>
          </template>
          <div class="placeholder">
            <p class="text-center text-muted">Information</p>
          </div>
        </b-card>
      </div>

      <div class="map-panel h-panel-half d-none">
        <b-card class="mt-2 setting-card panel-card" header-class="m-0 p-2 text-left"
                bg-variant="dark" text-variant="white">
          <template #header>
            <b-icon icon="map"></b-icon>
            <span class="ml-2">Streckenkarte</span>
            <slot name="header"></slot>
          </template>
          <div class="placeholder">
            <p class="text-center text-muted">Streckenkarte wird hier angezeigt</p>
          </div>
        </b-card>
      </div>

      <div class="bottom-panel h-panel">
        <b-card class="mt-2 setting-card panel-card" header-class="m-0 p-2 text-left"
                bg-variant="dark" text-variant="white">
          <template #header>
            <b-icon icon="pie-chart-fill"></b-icon>
            <span class="ml-2">Performance</span>
            <slot name="header"></slot>
          </template>
          <PerformanceMonitor />
        </b-card>
      </div>
      <div class="hardware-panel h-panel">
        <b-card class="mt-2 setting-card panel-card" header-class="m-0 p-2 text-right"
                bg-variant="dark" text-variant="white">
          <template #header>
            <span class="mr-2">System</span>
            <b-icon icon="pie-chart-fill"></b-icon>
            <slot name="header"></slot>
          </template>
          <HardwareInfo :hardware-info="hardwareInfo" />
        </b-card>
      </div>
    </div>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import lmwLogoUrl from "@/assets/lmw_logo.png";
import HardwareInfo from "@/components/widgets/HardwareInfo.vue";
import PerformanceMonitor from "@/components/pages/PerformanceMonitor.vue";

export default {
  name: 'KneeBoard',
  components: {PerformanceMonitor, HardwareInfo },
  props: {live: Boolean},
  data() {
    return {
      logoUrl: lmwLogoUrl,
      trackName: 'Unbekannt',
      currentLap: 0,
      totalLaps: 0,
      position: 0,
      bestLapTime: '--:--:---',
      notes: '',
      hardwareInfo: {
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
      },
      hardwareUpdateInterval: null,
    };
  },
  methods: {
    async fetchHardwareInfo() {
      const r = await getEelJsonObject(window.eel.get_hardware_status()())
      if (r.result) { this.hardwareInfo = r.data }
    },
    startHardwareMonitoring() {
      this.fetchHardwareInfo()
      this.hardwareUpdateInterval = setInterval(() => {
        this.fetchHardwareInfo()
      }, 2500); // Alle 2,5 Sekunden aktualisieren
    },
    stopHardwareMonitoring() {
      if (this.hardwareUpdateInterval) {
        clearInterval(this.hardwareUpdateInterval);
        this.hardwareUpdateInterval = null;
      }
    }
  },
  mounted() {
    this.startHardwareMonitoring();
  },
  beforeDestroy() {
    this.stopHardwareMonitoring();
  }
};
</script>

<style scoped>
.knee-board-container {
  border-radius: 8px;
  height: 91.65vh;
}

.knee-board-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 15px;
}

.panel-card {
  height: 100%;
}

.h-panel {
  height: 50.55vh;
}

.h-panel-half {
  height: calc(33.55vh * 0.5);
}

.info-panel {
  grid-column: 1 / 3;
  grid-row: 1;
}

.notes-panel {
  grid-column: 1;
  grid-row: 2;
}

.map-panel {
  grid-column: 2;
  grid-row: 2;
}

.bottom-panel {
  grid-column: 1;
  grid-row: 3;
}

.hardware-panel {
  grid-column: 2;
  grid-row: 3;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

@media (max-width: 768px) {
  /* need a breakpoint for the grid here */
}
</style>
