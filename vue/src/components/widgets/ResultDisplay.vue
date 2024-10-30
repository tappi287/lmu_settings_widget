<script>
import {getEelJsonObject} from "@/main";
import ResultDriver from "@/components/widgets/ResultDriver.vue";

export default {
  name: "ResultDisplay",
  props: {resultFile: String},
  components: {ResultDriver},
  data: function () {
    return {
      raceResultFields: [
        // {key: "expandRow", label: "", sortable: false, class: 'text-left'},
        {key: 'position', label: 'P', sortable: true, class: 'text-left'},
        {key: 'name', label: 'Name', class: 'text-left'},
        {key: 'fastest_lap_formatted', label: 'Best Lap', sortable: true, class: 'text-right'},
        {key: 'car_class', label: 'Class', class: 'text-right'},
        {key: 'class_position', label: 'P', class: 'text-left'},
        {key: 'car_number', label: '#', class: 'text-right'},
        {key: 'car_type', label: 'Car', class: 'text-right'},
        {key: 'finish_delta_laps_formatted', label: '', class: 'text-right secondary-info'},
        {key: 'finish_time_formatted', label: 'Time', class: 'text-right secondary-info'},
      ],
      incidentFields: [
          {key: 'et', label: 'Time', sortable: true, class: 'text-left'},
          {key: 'drivers', label: 'Drivers', sortable: true, class: 'text-left'},
          {key: 'text', label: 'Text', sortable: false, class: 'text-right'}
      ],
      incidentFilter: null,
      resultData: {}
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.isBusy = busy;
      this.$emit('set-busy', busy)
    },
    getResults: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.get_result_file(this.resultFile)())
      if (r.result) {
        this.resultData = r.data
      }
      if (!r.result) {
        this.makeToast(r.msg, 'danger', 'Get Results Error')
      }
      this.setBusy(false)
    },
    isPurpleLap(entry) {
      if (entry.fastest_lap_formatted === entry.purple_lap_formatted) { return "text-purple" }
      return ""
    },
    async gotoReplayTime(time) {
      await getEelJsonObject(window.eel.replay_time_command(time)())
    },
    async replayPlaybackCommand(command) {
      await getEelJsonObject(window.eel.replay_playback_command(command)())
    }
  },
  computed: {
    raceResultItems() {
      if (this.resultData.drivers === undefined) {
        return []
      }
      let resultItems = []
      for (const driver of this.resultData.drivers) {
        const item = driver
        // Use delta for non-leading cars
        if (driver.class_position !== 1) {
          item.finish_time_formatted = driver.finish_delta_formatted
        }
        // Fastest sectors
        let s1_sectors = []
        let s2_sectors = []
        let s3_sectors = []
        item.s1_fastest = ""
        item.s2_fastest = ""
        item.s3_fastest = ""
        for (const lap of driver.laps) {
          if (lap.s1 !== "-:--.---") { s1_sectors.push(lap.s1); }
          if (lap.s2 !== "-:--.---") { s2_sectors.push(lap.s2); }
          if (lap.s3 !== "-:--.---") { s3_sectors.push(lap.s3); }
        }
        if (s1_sectors.length > 0 && s2_sectors.length > 0 && s3_sectors.length > 0) {
          item.s1_fastest = s1_sectors.sort()[0]
          item.s2_fastest = s2_sectors.sort()[0]
          item.s3_fastest = s3_sectors.sort()[0]
        }

        // Add to results
        resultItems.push(
            item
        )
      }
      return resultItems
    }
  },
  mounted() {
    this.getResults()
  }
}
</script>

<template>
  <div>
      <b-button-group title="Replay Controls" size="sm" class="text-center text-monospace text-bold mb-4">
        <b-button @click="replayPlaybackCommand(0)" variant="rf-blue" title="Skip to Start">
          |<
        </b-button>
        <b-button @click="replayPlaybackCommand(2)" variant="rf-secondary" title="Fast Reverse" >
          <<<
        </b-button>
        <b-button @click="replayPlaybackCommand(3)" variant="rf-secondary" title="Reverse Scan">
          <<
        </b-button>
        <b-button @click="replayPlaybackCommand(4)" variant="rf-secondary" title="Play Reverse">
          <
        </b-button>
        <b-button @click="replayPlaybackCommand(5)" variant="rf-secondary" title="Reverse Slow-Mo">
          <|
        </b-button>
        <b-button @click="replayPlaybackCommand(6)" variant="rf-secondary" title="Pause">
          ||
        </b-button>
        <b-button @click="replayPlaybackCommand(7)" variant="rf-secondary" title="Slow-mo">
          |>
        </b-button>
        <b-button @click="replayPlaybackCommand(8)" variant="rf-secondary" title="Play">
          >
        </b-button>
        <b-button @click="replayPlaybackCommand(9)" variant="rf-secondary" title="Scan Forward">
          >>
        </b-button>
        <b-button @click="replayPlaybackCommand(10)" variant="rf-secondary" title="Fast Forward">
          >>>
        </b-button>
        <b-button @click="replayPlaybackCommand(1)" variant="rf-blue" title="Skip to End">
          >|
        </b-button>
      </b-button-group>
    <b-tabs align="left" no-fade>
      <b-tab title="Session Results" title-link-class="btn-secondary pt-1 pb-1">
        <!-- RESULT -->
        <b-table :items="raceResultItems" :fields="raceResultFields"
                 details-td-class="result-td-details"
                 sort-by="position" no-sort-reset sort-icon-left
                 table-variant="dark" small borderless
                 class="server-list" thead-class="text-white"
                 ref="resultTable"
        >
          <template #cell(name)="row">
            <b-button size="sm" @click="row.toggleDetails" title="Show Laptimes"
                      class="text-light m-0 mr-2 no-border no-bg">
              <b-icon :icon="row.detailsShowing ? 'caret-down-fill': 'caret-right-fill'"
                      variant="secondary" shift-v="1"/>
              {{ row.item.name }}
            </b-button>
          </template>
          <template #cell(fastest_lap_formatted)="row">
            <span :class="isPurpleLap(row.item)">{{ row.item.fastest_lap_formatted }}</span>
          </template>
          <!-- LAP TIMES -->
          <template #row-details="detail">
            <ResultDriver :driver="detail.item" />
          </template>
        </b-table>
      </b-tab>
      <!-- INCIDENTS -->
      <b-tab title="Incidents" title-link-class="btn-secondary pt-1 pb-1">
        <b-table :items="resultData.entries"
                 :fields="incidentFields"
                 :filter="incidentFilter"
                 sort-by="et" no-sort-reset sort-icon-left
                 table-variant="dark" small borderless
                 class="server-list" thead-class="text-white">
          <template #cell(et)="row">
            <b-link class="text-monospace" @click="gotoReplayTime(row.item.et)" title="Jump to time in Replay">
              {{ row.item.et }}
            </b-link>
          </template>
          <!-- A custom formatted header cell for field 'name' -->
          <template #head(drivers)="data">
            <span class="mr-1">{{ data.label }}</span>
            <template v-if="incidentFilter!==null">
              <b-link @click="incidentFilter=null" class="float-right text-warning">
                Clear Filter
              </b-link>
            </template>
          </template>
          <template #cell(drivers)="row">
            <b-link v-for="(d, idx) in row.item.drivers" :key="idx"
                    @click="incidentFilter=d" title="Filter by this Driver"
                    class="mr-1 small" variant="secondary">
              {{ d }}
            </b-link>
          </template>
          <template #cell(text)="row">
            <span class="small">{{ row.item.text }}</span>
          </template>
        </b-table>
      </b-tab>
    </b-tabs>
  </div>
</template>

<style scoped>
.text-purple {
  color: #e327db;
}
.result-td-details { padding: 0; margin: 0; border: none; }
</style>