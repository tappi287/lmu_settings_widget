<template>
  <div class="knee-board-container">
    <b-input-group size="sm">
      <b-input-group-prepend>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          KneeBoard
        </b-input-group-text>
      </b-input-group-prepend>

      <!-- Spacer -->
      <div class="form-control bg-transparent no-border" />

      <!-- Preset Selection -->
      <div class="mt-1">
        <b-input-group size="sm">
          <b-input-group-prepend>
            <b-input-group-text class="bg-transparent no-border title text-white pl-0">
              <b-link @click="showHelp=true">Help</b-link>
            </b-input-group-text>
          </b-input-group-prepend>
        </b-input-group>
      </div>
    </b-input-group>

    <div class="knee-board-inner-container">
      <div class="knee-board-content" :class="showHelp ? 'knee-board-content-fade' : ''">
        <div class="info-panel">
          <b-card class="mt-2 setting-card h-100" header-class="m-0 p-2 text-left"
                  bg-variant="dark" text-variant="white">
            <template #header>
              <b-icon icon="tv"></b-icon>
              <span class="ml-2">Pit Strategy [Placeholder]</span>
              <slot name="header"></slot>
            </template>
            <b-row class="text-left" align-v="center">
              <b-col>
                Fuel
              </b-col>
              <b-col>
                <b-progress>
                  <b-progress-bar value="97">
                    <span>97%</span>
                  </b-progress-bar>
                </b-progress>
              </b-col>
              <b-col>
                Fuel per Lap Average
              </b-col>
              <b-col>
                <b>2.94%</b>
              </b-col>
              <div class="w-100"></div>
              <b-col>
                Pit in Lap
              </b-col>
              <b-col>
                16
              </b-col>
              <b-col>
                Time until Empty
              </b-col>
              <b-col>
                02:12:23
              </b-col>
            </b-row>
          </b-card>
        </div>

        <!-- Performance Monitor -->
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

        <!-- Hardware Monitor -->
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

      <!-- Help Overlay -->
      <b-overlay :show="showHelp" no-wrap variant="transparent" blur="1px" size="xl">
        <template v-slot:overlay>
          <KneeBoardHelp @close="showHelp=false"></KneeBoardHelp>
        </template>
      </b-overlay>
    </div>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import lmwLogoUrl from "@/assets/lmw_logo.png";
import HardwareInfo from "@/components/widgets/HardwareInfo.vue";
import PerformanceMonitor from "@/components/pages/PerformanceMonitor.vue";
import KneeBoardHelp from "@/components/pages/KneeBoardHelp.vue";

export default {
  name: 'KneeBoard',
  components: {KneeBoardHelp, PerformanceMonitor, HardwareInfo },
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
      showHelp: true,
      openKneeboardInstalled: false
    };
  },
  methods: {
    async fetchHardwareInfo() {
      const r = await getEelJsonObject(window.eel.get_hardware_status()())
      if (r.result) { this.hardwareInfo = r.data }
    },
    async getOpenKneeBoardLocation() {
      const r = await getEelJsonObject(window.eel.get_open_kneeboard_location()())
      if (r.result) { this.openKneeboardInstalled = true }
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
  async mounted() {
    this.startHardwareMonitoring();
    await this.getOpenKneeBoardLocation();
    if (this.openKneeboardInstalled) { this.showHelp = false }
  },
  beforeDestroy() {
    this.stopHardwareMonitoring();
  }
};
</script>

<style src="../../assets/kneeboard.css">

</style>
