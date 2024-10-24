<script xmlns="">
import {getEelJsonObject} from "@/main";

export default {
  name: "ResultDisplay",
  props: {driver: Object},
  data: function () {
    return {
      driverFields: [
        {key: "num", label: "#", sortable: true, class: 'text-left'},
        {key: "p", label: "Position", class: 'text-left'},
        {key: "laptime_formatted", label: "laptime", sortable: true, class: 'text-left'},
        {key: "s1", label: "S1", sortable: true, class: 'text-left'},
        {key: "s2", label: "S2", sortable: true, class: 'text-left'},
        {key: "s3", label: "S3", sortable: true, class: 'text-left'},
        {key: "pit", label: "Pit", class: 'text-right'},
        {key: "topspeed", label: "Top Speed", class: 'text-right'},
        {key: "fcompound", label: "Fronts", class: 'text-right'},
        {key: "rcompound", label: "Rears", class: 'text-right'},
      ],
      selectedRow: null,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.isBusy = busy;
      this.$emit('set-busy', busy)
    }
  }
}
</script>

<template>
  <b-table :items="driver.laps" :fields="driverFields"
           sort-by="num" no-sort-reset sort-icon-left
           table-variant="dark" small borderless
           class="server-list" thead-class="text-white">
    <template #cell(pit)="row">
      {{ row.item.pit ? 'In Pit' : '-' }}
    </template>
  </b-table>
</template>

<style scoped>

</style>