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

      <div class="notes-panel">
        <b-card class="mt-2 setting-card" header-class="m-0 p-2 text-left"
                bg-variant="dark" text-variant="white">
          <template #header>
            <b-icon icon="map"></b-icon>
            <span class="ml-2">Info</span>
            <slot name="header"></slot>
          </template>
          <div class="placeholder">
            <p class="text-center text-muted">Information</p>
          </div>
        </b-card>
      </div>

      <div class="map-panel">
        <b-card class="mt-2 setting-card" header-class="m-0 p-2 text-left"
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
      <div class="hardware-panel">
        <b-card class="mt-2 setting-card" header-class="m-0 p-2 text-left"
                bg-variant="dark" text-variant="white">
          <template #header>
            <b-icon icon="pie-chart-fill"></b-icon>
            <span class="ml-2">System</span>
            <slot name="header"></slot>
          </template>
          <div class="placeholder">
            <p class="text-center text-muted">Hardware Info</p>
          </div>
        </b-card>
      </div>
      <div class="bottom-panel">
        <b-card class="mt-2 setting-card" header-class="m-0 p-2 text-right"
                bg-variant="dark" text-variant="white">
          <template #header>
            <span class="mr-2">Info</span>
            <b-icon icon="pie-chart-fill"></b-icon>
            <slot name="header"></slot>
          </template>
          <div class="placeholder">
            <p class="text-center text-muted">Hardware Info</p>
          </div>
        </b-card>
      </div>
    </div>
  </div>
</template>

<script>
import lmwLogoUrl from "@/assets/lmw_logo.png";

export default {
  name: 'KneeBoard',
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
    };
  },
  methods: {
    updateRaceInfo(data) {
      if (data) {
        this.trackName = data.trackName || this.trackName;
        this.currentLap = data.currentLap || this.currentLap;
        this.totalLaps = data.totalLaps || this.totalLaps;
        this.position = data.position || this.position;
        this.bestLapTime = data.bestLapTime || this.bestLapTime;
      }
    },
    saveNotes() {
      // Hier Code zum Speichern der Notizen implementieren
      console.log('Notizen gespeichert:', this.notes);
    }
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

.hardware-panel {
  grid-column: 1;
  grid-row: 3;
}

.bottom-panel {
  grid-column: 2;
  grid-row: 3;
}

.placeholder {
  height: 27vh;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}
</style>
