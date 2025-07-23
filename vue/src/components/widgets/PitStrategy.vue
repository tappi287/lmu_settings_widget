<script>
export default {
  name: 'HardwareInfo',
  data() {
    return {
      noData: true
    };
  }
}
</script>

<template>
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
</template>

<style scoped>

</style>