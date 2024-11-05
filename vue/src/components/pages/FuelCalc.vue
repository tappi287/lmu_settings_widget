<script>
import lmwLogoUrl from "@/assets/lmw_logo.png"
import {divMod} from "@/main.js";

export default {
  name: "FuelCalc",
  data: function () {
    return {
      resultPresets: [
          12, 16, 24, 30, 80, 100, 120
      ],
      trackPresets: [
        {name: "Portimão GTE", consumption: 2.86, lapTime: 110.5},
        {name: "Portimão LMP2", consumption: 2.45, lapTime: 96.15},
        {name: "Portimão Hy", consumption: 2.99, lapTime: 88.123},
        {name: "Imola GTE", consumption: 3.2, lapTime: 107.891}
      ],
      selectedPreset: 0,
      lapMinutes: 1,
      lapSeconds: 23,
      lapThousands: 456,
      fuelConsumption: 2.5,
      raceHours: 1,
      raceMinutes: 30,
      raceLaps: 0,
      extraLaps: 1,
      logoUrl: lmwLogoUrl,
      isDev: import.meta.env.DEV,
    }
  },
  methods: {
    setLapTime(lapTime) {
      const _r1 = divMod(lapTime * 1000, 1000)
      let s = _r1[0]
      let ms = _r1[1]
      const _r2 = divMod(s, 60)
      let m = _r2[0]
      s = _r2[1]
      const _r3 = divMod(m, 60)
      m = _r3[1]

      this.lapMinutes = m
      this.lapSeconds = s
      this.lapThousands = ms
    },
    selectTrackPreset(idx) {
      this.selectedPreset = parseInt(idx)
      this.setLapTime(this.trackPresets[idx].lapTime)
      this.fuelConsumption = this.trackPresets[idx].consumption
    },
    raceLapsUpdate() {
      const duration = this.currentLapTime * this.raceLaps
      const _r = divMod(duration, 60)
      const _r2 = divMod(_r[0], 60)
      this.raceHours = _r2[0]
      this.raceMinutes = _r2[1]
    },
    raceDurationUpdate() {
      this.raceLaps = Math.ceil(this.currentRaceDuration / this.currentLapTime)
    },
    calculateFuel(lapTime, duration, fuel, extraLaps) {
      /* Simple fuel estimation by number of laps for given fuel consumption per lap */
      const laps = Math.ceil(duration / lapTime) + extraLaps
      const fuelAmount = Math.round(laps * fuel)
      return [fuelAmount, laps]
    },
    presetCalc(r) {
      return this.calculateFuel(
          parseFloat(this.currentLapTime),
          r * 60,
          parseFloat(this.fuelConsumption),
          parseFloat(this.extraLaps)
      )
    },
    paddedNum(num, padding, padString="0") {
      return String(num).padStart(padding, padString)
    }
  },
  computed: {
    currentTrackPreset() {
      return this.trackPresets[this.selectedPreset]
    },
    currentLapTime() {
      const lapMinInSeconds = this.lapMinutes * 60
      const lapSeconds = this.lapSeconds
      const lapThousandsInSeconds = this.lapThousands / 1000
      return lapMinInSeconds + lapSeconds + lapThousandsInSeconds
    },
    currentRaceDuration() {
      const raceMinutesInSeconds = this.raceMinutes * 60
      const raceHoursInSeconds = this.raceHours * 3600
      return raceMinutesInSeconds + raceHoursInSeconds
    },
    currentRaceDurationMinutes() {
      const raceMinutes = this.raceMinutes
      const raceHoursInMinutes = this.raceHours * 60
      return raceMinutes + raceHoursInMinutes
    },
    currentFuelCalculation() {
      const fuelResult = this.calculateFuel(
          this.currentLapTime,
          this.currentRaceDuration,
          this.fuelConsumption,
          this.extraLaps
      )
      const fuelAmount = fuelResult[0]
      const estimatedLaps = fuelResult[1]

      return [fuelAmount, estimatedLaps]
    }
  },
  created() {
    this.selectTrackPreset(0)
  }
}
</script>

<template>
  <div id="fuel-calc">
    <b-input-group size="sm">
      <b-input-group-prepend>
        <div class="pl-0 pr-1 lmu-con position-relative bg-transparent">
          <b-img width=".3rem" class="lmu-icon" :src="logoUrl"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          Fuel Calculator
        </b-input-group-text>
      </b-input-group-prepend>
    </b-input-group>
    <b-card class="setting-card mt-2 mb-2 text-left p-3" bg-variant="dark" text-variant="white" footer-class="p-2">
      <template #header>
        <b-row>
          <b-col sm="4">
            <b-icon shift-v="-2" icon="calculator-fill"></b-icon>
            <span class="ml-2 align-middle">Presets</span>
          </b-col>
          <b-col sm="8">
            <b-dropdown size="sm" :text="currentTrackPreset.name">
              <b-dropdown-item size="sm" v-for="(p, idx) in trackPresets" :key="idx"
                               @click="selectTrackPreset(idx)">
                {{ p.name }}
              </b-dropdown-item>
            </b-dropdown>
          </b-col>
        </b-row>
      </template>

      <!-- Lap Time -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="speedometer"></b-icon>
          <label class="ml-2 m-0 p-0 align-middle" for="inline-form-custom-select-pref">Average lap time</label>
        </b-col>
        <b-col sm="8">
          <b-form inline>
            <b-form-input id="inline-form-custom-lap-minute" class="mr-sm-2" size="sm"
                          type="number" min="0" max="15" number v-model="lapMinutes"/>
            :
            <b-form-input id="inline-form-custom-lap-seconds" class="mr-sm-2 ml-sm-2" size="sm"
                          type="number" min="0" max="59" number v-model="lapSeconds"/>
            .
            <b-form-input id="inline-form-custom-lap-thousands" class="mr-sm-2 ml-sm-2" size="sm"
                          type="number" min="0" max="999" number v-model="lapThousands"/>
            <span class="text-monospace small text-muted align-middle">({{ currentLapTime }}s)</span>
          </b-form>
        </b-col>
      </b-row>

      <!-- Fuel Consumption -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="funnel"></b-icon>
          <span class="ml-2 align-middle">Average fuel consumption</span>
        </b-col>
        <b-col sm="8">
          <b-form inline>
            <b-form-input id="inline-form-fuel-consume" type="number" size="sm" class="mr-sm-2"
                          number v-model="fuelConsumption" min="0.0" max="99.0" step="0.1"/>
            <span class="align-middle">l</span>
          </b-form>
        </b-col>
      </b-row>

      <!-- Race Duration -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="clock"></b-icon>
          <span class="ml-2 align-middle">Race Duration</span>
        </b-col>
        <b-col sm="8">
          <b-form inline @change="raceDurationUpdate">
            <b-form-input id="inline-form-custom-lap-minute" class="mr-sm-2" size="sm"
                          type="number" min="0" max="999" number v-model="raceHours"/>
            h
            <b-form-input id="inline-form-custom-lap-seconds" class="mr-sm-2 ml-sm-2" size="sm"
                          type="number" min="0" max="59" number v-model="raceMinutes"/>
            min
            <span class="ml-4 text-monospace small text-muted align-middle">({{ currentRaceDuration }}s)</span>
          </b-form>
        </b-col>
      </b-row>
      <b-row>
        <b-col sm="4" />
        <b-col sm="8">
          <b-form inline @change="raceLapsUpdate">
            <b-form-input id="inline-form-custom-lap-minute" class="mr-sm-2" size="sm"
                          type="number" min="0" max="9999" number v-model="raceLaps"/>
            laps
          </b-form>
        </b-col>
      </b-row>

      <!-- Extra Laps -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="plus-circle-dotted"></b-icon>
          <span class="ml-2 align-middle">Out/in laps</span>
        </b-col>
        <b-col sm="8">
          <b-form inline>
            <b-form-input id="inline-form-fuel-consume" type="number" size="sm" class="mr-sm-2"
                          number v-model="extraLaps" min="0" max="99"/>
          </b-form>
        </b-col>
      </b-row>

      <template #footer>
        <!-- Result -->
        <b-row class="mt-4 mb-2">
          <b-col sm="4">
            <b-icon shift-v="-3" icon="receipt"></b-icon>
            <span class="ml-2 align-middle">Results</span>
          </b-col>
          <b-col sm="8" class="text-monospace text-left">
            <span class="mr-4">{{ paddedNum(currentRaceDurationMinutes, 3) }} mins</span>
            <span class="mr-4">{{ paddedNum(currentFuelCalculation[0], 3, " ") }} l</span>
            <span class="mr-4">{{ paddedNum(currentFuelCalculation[1], 3, "0") }} laps</span>
          </b-col>
        </b-row>
        <!-- Preset Results -->
        <b-row v-for="(r, idx) in resultPresets" :key="idx"
               class="text-muted">
          <b-col sm="4" />
          <b-col sm="8" class="text-monospace text-left">
            <span class="mr-4">{{ paddedNum(r, 3) }} mins</span>
            <span class="mr-4">{{ paddedNum(presetCalc(r)[0], 3, " ") }} l</span>
            <span class="mr-4">{{ paddedNum(presetCalc(r)[1], 3, "0") }} laps</span>
          </b-col>
        </b-row>
      </template>
    </b-card>
  </div>
</template>

<style scoped>
.lmu-icon {
  width: 2.075rem;
}

.lmu-con {
  margin-top: .1rem;
}
</style>