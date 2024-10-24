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
        {key: 'class_position', label: 'Class P', class: 'text-left'},
        {key: 'name', label: 'Name', class: 'text-left'},
        {key: 'fastest_lap_formatted', label: 'Best Lap', sortable: true, class: 'text-right'},
        {key: 'car_class', label: 'Class', class: 'text-right'},
        {key: 'car_number', label: '#', class: 'text-right'},
        {key: 'car_type', label: 'Car', class: 'text-right'},
        {key: 'finish_delta_laps_formatted', label: '', class: 'text-right secondary-info'},
        {key: 'finish_time_formatted', label: 'Time', class: 'text-right secondary-info'},
      ],
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
        if (driver.class_position !== 1) {
          item.finish_time_formatted = driver.finish_delta_formatted
        }
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
    <b-tabs>
      <b-tab title="Result">
        <b-table :items="raceResultItems" :fields="raceResultFields"
                 sort-by="position" no-sort-reset sort-icon-left
                 table-variant="dark" small borderless
                 class="server-list" thead-class="text-white"
                 ref="resultTable"
        >
          <template #cell(name)="row">
            <b-button size="sm" @click="row.toggleDetails" class="text-light m-0 mr-2 no-border no-bg">
              <b-icon :icon="row.detailsShowing ? 'caret-down-fill': 'caret-right-fill'"
                      variant="secondary" shift-v="1"/>
            </b-button>
            {{ row.item.name }}
          </template>
          <template #row-details="detail">
            <ResultDriver :driver="detail.item"/>
          </template>
        </b-table>
      </b-tab>
    </b-tabs>
  </div>
</template>

<style scoped>

</style>