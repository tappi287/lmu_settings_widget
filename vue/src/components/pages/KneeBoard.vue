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
      <div class="knee-board-content" :class="showHelp || !metricsEnabled ? 'knee-board-content-fade' : ''">
        <!-- Placeholder PitStrategy -->
        <div class="info-panel d-none">
          <PitStrategy />
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

      <!-- Spacer <div style="height: 30vh;"></div> -->

      <!-- Enable Metrics Overlay -->
      <b-overlay no-wrap :show="!metricsEnabled && !showHelp" variant="transparent">
        <template v-slot:overlay>
          <b-card class="rounded" bg-variant="dark" text-variant="white">
            <b-checkbox switch @change="switchMetrics">Enable Metrics</b-checkbox>
            <b-card-text class="mt-4">
              Enable performance metric capturing with the PresentMon service.<br />
              <b-link @click="showHelp = true">More Info...</b-link>
            </b-card-text>
          </b-card>
        </template>
      </b-overlay>
    </div>
    <b-overlay class="kneeboard-help" no-wrap :show="showHelp" variant="transparent" blur="1px">
      <template v-slot:overlay>
        <KneeBoardHelp @close="showHelp=false"></KneeBoardHelp>
      </template>
    </b-overlay>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import lmwLogoUrl from "@/assets/lmw_logo.png";
import HardwareInfo from "@/components/widgets/HardwareInfo.vue";
import PerformanceMonitor from "@/components/pages/PerformanceMonitor.vue";
import KneeBoardHelp from "@/components/pages/KneeBoardHelp.vue";
import PitStrategy from "@/components/widgets/PitStrategy.vue";
import PreferencesPage from "@/components/pages/PreferencesPage.vue";

export default {
  name: 'KneeBoard',
  components: {KneeBoardHelp, PerformanceMonitor, HardwareInfo, PitStrategy },
  props: {live: Boolean, prefs: PreferencesPage},
  data() {
    return {
      logoUrl: lmwLogoUrl,
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
      openKneeboardInstalled: false,
      metricsEnabled: false
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
    async switchMetrics(enableMetrics) {
      if (this.prefs !== undefined) {
        if (enableMetrics) {
          if (this.prefs.appModules.indexOf("show_hardware_info") === -1) {
            this.prefs.appModules.push("show_hardware_info");
            await this.prefs.save()
          }
        } else {
          const index = this.prefs.appModules.indexOf("show_hardware_info");
          if (index !== -1) {
            this.prefs.appModules.splice(index, 1);
            await this.prefs.save()
          }
        }
        this.metricsEnabled = enableMetrics
      }
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
    this.showHelp = !this.live
    if (this.openKneeboardInstalled) { this.showHelp = false }
    if (this.prefs !== undefined) {
      this.metricsEnabled = this.prefs.appModules.indexOf("show_hardware_info") !== -1
    }
  },
  beforeDestroy() {
    this.stopHardwareMonitoring();
  }
};
</script>

<style src="../../assets/kneeboard.css">

</style>
