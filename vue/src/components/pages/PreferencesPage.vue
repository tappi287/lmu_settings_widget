<template>
  <div v-cloak v-if="visible" id="settings" class="position-relative mb-5 text-left">
    <b-input-group class="pb-2" size="sm">
      <b-input-group-prepend>
        <div class="pl-0 pr-1 rpl-con position-relative bg-transparent">
          <b-img width=".3rem" class="rpl-icon" :src="lmwLogoUrl"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          App Preferences
        </b-input-group-text>
      </b-input-group-prepend>

      <!-- Spacer -->
      <div class="form-control bg-transparent no-border"></div>
    </b-input-group>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h5 class="mb-0"><span class="title">General</span></h5>
      </template>

      <b-row v-for="option in appOptions" no-gutters>
        <b-form-checkbox
          v-model="appModules"
          :key="option.value"
          :value="option.value"
          @change="save"
        >
          <b-col cols="4"><b>{{ option.text }}</b></b-col>
          <b-col class="text-white-50">{{ option.description }}</b-col>
        </b-form-checkbox>
      </b-row>
      <!--
      <b-checkbox-group :options="appOptions" v-model="appModules" @change="save" />
      -->
    </b-card>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h5 class="mb-0"><span class="title">Autostart</span></h5>
      </template>
      <b-card-text>
        Which applications to automatically launch along with the game. This detects already running applications.
      </b-card-text>

      <b-checkbox-group :options="appAutostartOptions" v-model="appAutostart" @change="save" />
    </b-card>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h5 class="mb-0"><span class="title">Dashboard</span></h5>
      </template>

      <b-checkbox-group :options="dashboardOptions" v-model="dashboardModules" @change="save" />

      <b-card-text class="mt-3">
        Choose what you would like to see on your dashboard.
      </b-card-text>

    </b-card>

    <b-card class="setting-card" bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">Le Mans Ultimate Location</span></h6>
      </template>
      <RfLocation />
    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import RfLocation from "@/components/widgets/RfLocation.vue";
import lmwLogoUrl from "@/assets/lmw_logo.png"

export default {
  name: "PreferencesPage",
  components: {RfLocation},
  props: {visible: Boolean},
  data: function () {
    return {
      dashboardModules: ['img', 'favs', 'cont'],
      dashboardOptions: [
          // {text: 'Play Image Slideshow', value: 'img'},
          // {text: 'Show Server Favourites', value: 'favs'},
          {text: 'Show Controller Devices', value: 'cont'}
      ],
      appModules: ['audio', 'edge_preferred'],
      appAutostart: [],
      appAutostartOptions: [
          {text: 'OpenKneeboard', value: 'kneeboard'},
      ],
      appOptions: [
        {text: 'Enable Audio', value: 'audio', description: 'Weather to play audio feedback when using certain actions within the app.'},
        {text: 'Prefer Edge Browser', value: 'edge_preferred', description: 'Prefer the Windows builtin Chromium Edge browser over Google Chrome to render this app. Changes apply after an app restart.'},
        {text: 'Performance Monitoring', value: 'show_hardware_info', description: 'Weather to collect hardware stats like CPU/GPU Load and performance metrics with PresentMon displayed on the Kneeboard page.'},
      ],
      lmwLogoUrl: lmwLogoUrl
    }
  },
  methods: {
    async save () {
      let appPref = {}
      appPref['dashboardModules'] = this.dashboardModules
      appPref['appModules'] = this.appModules
      appPref['autostart'] = this.appAutostart

      await getEelJsonObject(window.eel.save_app_preferences(appPref)())
    },
    async load () {
      const r = await getEelJsonObject(window.eel.load_app_preferences()())
      if (r.result) {
        const appPref = r.preferences
        if ('dashboardModules' in appPref) {
          this.dashboardModules = appPref['dashboardModules']
        }
        if ('appModules' in appPref) {
          this.appModules = appPref['appModules']
        }
        if ('autostart' in appPref) {
          this.appAutostart = appPref['autostart']
        }
      }
    }
  },
  async created() {
    await this.load()
  }
}
</script>

<style scoped>
  .rpl-icon { width: 2.075rem; }
  .rpl-con { margin-top: .1rem; }
</style>