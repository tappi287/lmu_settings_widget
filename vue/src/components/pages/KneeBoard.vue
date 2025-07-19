<template>
  <div class="knee-board-container">
    <h2>KneeBoard</h2>
    <div class="knee-board-content">
      <div class="info-panel">
        <b-card title="Renninfo" class="mb-3">
          <b-row>
            <b-col md="6">
              <p><strong>Strecke:</strong> {{ trackName }}</p>
              <p><strong>Runden:</strong> {{ currentLap }} / {{ totalLaps }}</p>
            </b-col>
            <b-col md="6">
              <p><strong>Position:</strong> {{ position }}</p>
              <p><strong>Beste Rundenzeit:</strong> {{ bestLapTime }}</p>
            </b-col>
          </b-row>
        </b-card>
      </div>

      <div class="notes-panel">
        <b-card title="Notizen" class="mb-3">
          <b-form-textarea
            v-model="notes"
            placeholder="Notizen hier eingeben..."
            rows="4"
            max-rows="8"
          ></b-form-textarea>
        </b-card>
      </div>

      <div class="map-panel">
        <b-card title="Streckenkarte">
          <div class="track-map-placeholder">
            <p class="text-center text-muted">Streckenkarte wird hier angezeigt</p>
          </div>
        </b-card>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KneeBoard',
  data() {
    return {
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

.track-map-placeholder {
  height: 200px;
  background-color: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}
</style>
