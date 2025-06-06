<template>
  <div>
    <b-button-group>
      <b-dropdown variant="rf-blue-light" :size="btnSizeString" right split @click="launchButton">
        <template #button-content>
          <div class="rounded-right">
            <b-icon shift-v="-0.5" icon="play"></b-icon>
            {{ buttonText }}
            <span class="ml-1" v-if="displayLive">
              <b-icon shift-v="3" font-scale="0.9" :icon="live ? 'circle-fill' : 'circle'" :variant="live ? 'success' : 'rf-blue'"/>
            </span>
          </div>
        </template>
        <b-dropdown-item v-for="(item, key, index) in launchMethods" :key="index"
                         @click="launchRfactor(Number(key))" v-b-popover.right.hover="item.desc">
          {{ item.name }}
        </b-dropdown-item>
        <!--
        <b-dropdown-item v-if="chooseContent" @click="$emit('show-content')">
          Choose Tracks and Cars
        </b-dropdown-item>
        -->
      </b-dropdown>
    </b-button-group>
    <!-- Device Warning -->
    <b-modal v-model="showDeviceModal" centered size="md" modal-class="launch-modal">
      <template #modal-title>
        <b-icon icon="exclamation-triangle-fill" shift-v="-0.45" variant="primary"></b-icon>
        <span class="ml-2">Device Warning</span>
      </template>
      <p class="small">
        These Controller Devices were detected as <i>not</i> connected.
      </p>
      <p v-for="name in deviceList" :key="name">{{ name }}</p>
      <p class="small">
        <i>
          Go to
          <b-link @click="$eventHub.$emit('navigate', 2); showDeviceModal=false">
            Control Settings
          </b-link>
          and disable the check boxes in the <b>Controller Devices</b>
          Section if you do not want to see this warning.
        </i>
      </p>
      <template #modal-footer>
        <div class="d-block text-right">
          <b-button variant="rf-blue-light" @click="launchAnyway" class="mr-2">Launch anyway</b-button>
          <b-button variant="secondary" @click="abort">Abort</b-button>
        </div>
      </template>
    </b-modal>
    <!-- First Launch -->
    <b-modal v-model="showLaunchModal" centered size="md" modal-class="launch-modal">
      <template #modal-title>
        <b-icon icon="question-square-fill" shift-v="-0.45" variant="primary"></b-icon>
        <span class="ml-2">Choose Launch Option</span>
      </template>
      <div class="text-center">
        <div v-for="(item, key, index) in launchMethods" :key="index">
          <b-button variant="rf-blue-light" class="w-75 mt-3"
                    :size="btnSizeString" @click="launchFromModal(Number(key))"
                    v-b-popover.auto.hover="item.desc">
            <b-icon shift-v="-0.0" icon="play"></b-icon>
            <span class="ml-2">{{ item.name }}</span>
          </b-button>
        </div>
      </div>
      <p class="small mt-4">
        Launch option will be remembered the next time you press the launch button. If you want to change the preferred
        option, use the dropdown menu next to the launch button or use the Launch Option inside Graphics Presets
        to choose a different option.<br/>
      </p>
      <template #modal-footer>
        <div class="d-block text-right">
          <b-button variant="secondary" @click="abort">Abort</b-button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import {getEelJsonObject, sleep} from "@/main.js";
// --- </ Prepare receiving rfactor live events
window.eel.expose(rfactorLiveFunc, 'rfactor_live')

async function rfactorLiveFunc(event) {
  const liveEvent = new CustomEvent('rfactor-live-event', {detail: event})
  window.dispatchEvent(liveEvent)
}

// --- />

export default {
  name: "LaunchRfactorBtn",
  props: {
    text: String,
    btnSize: String,
    server: Object,
    displayLive: Boolean,
    chooseContent: Boolean,
    compact: Boolean
  },
  data: function () {
    return {
      live: false, size: "sm", devicesReady: true, deviceList: [], currentGfxPreset: {},
      showDeviceModal: false, showLaunchModal: false, lastMethod: 0, checkDevices: true,
      launchMethods: {
        2: {name: 'Launch via Steam in VR'},
        3: {
          name: 'Launch via Exe in VR',
          desc: 'If you have a dedicated Server running. This is the method to ' +
              'launch LMU anyway. Make sure you have configured your WebUI ports correctly.'
        },
        0: {name: 'Launch via Steam'},
        1: {
          name: 'Launch via Exe',
          desc: 'If you have a dedicated Server running. This is the method to ' +
              'launch LMU anyway. Make sure you have configured your WebUI ports correctly.'
        }
      }
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
    getPresetLaunchOption() {
      if (this.currentGfxPreset.video_settings === undefined) {
        return undefined
      }
      let launchMethodValue = 0

      this.currentGfxPreset.video_settings.options.forEach(option => {
        if (option.key === 'Launch') {
          launchMethodValue = option.value
        }
      })
      return launchMethodValue
    },
    updateRfactorState: function (event) {
      this.live = event.detail
      this.$emit('update-live', this.live)
    },
    setDeviceState: function (event) {
      this.devicesReady = event.devicesReady;
      this.deviceList = event.deviceList;
    },
    launchButton: async function () {
      /* Regular Launch button without drop down option */
      this.$eventHub.$emit('getCurrentGfxPreset')
      await sleep(100)
      await this.launchRfactor(this.getPresetLaunchOption())
    },
    launchRfactor: async function (method) {
      if (typeof (method) !== 'number') {
        method = undefined
        let saved_method = await getEelJsonObject(window.eel.get_last_launch_method()())
        if (typeof (saved_method) === 'number') {
          method = saved_method
        } else {
          this.showLaunchModal = true
          return
        }
      }
      if (!this.devicesReady && this.checkDevices) {
        this.showDeviceModal = true
        this.lastMethod = method
        return
      }
      // Give BackEnd some time to write settings
      this.$emit('launch')
      await sleep(200)

      let r = await getEelJsonObject(window.eel.run_rfactor(this.serverData, method)())
      if (r !== undefined && r.result) {
        this.makeToast(`${this.launchMethods[method].name}. Do not change settings here while ` +
            'the game is running. The game would overwrite those settings anyway upon exit.',
            'success', 'Le Mans Ultimate Launch')
      } else {
        this.makeToast('Could not launch Le Mans Ultimate.exe', 'danger',
            'Le Mans Ultimate Launch')
        this.$emit('launch-failed')
      }
    },
    abort() {
      this.showDeviceModal = false;
      this.showLaunchModal = false
    },
    launchAnyway() {
      this.showDeviceModal = false
      this.checkDevices = false
      this.launchRfactor(this.lastMethod)
      this.checkDevices = true
    },
    launchFromModal(method) {
      this.showLaunchModal = false
      this.launchRfactor(method)
    },
    setCurrentGfxPreset(preset) {
      this.currentGfxPreset = preset
    }
  },
  computed: {
    serverData: function () {
      if (this.server !== undefined) {
        return this.server
      }
      // make sure we send Python: None object
      return undefined
    },
    buttonText: function () {
      if (this.text !== undefined) {
        return this.text
      }
      return 'Start Le Mans Ultimate'
    },
    btnSizeString: function () {
      if (this.btnSize === undefined) {
        return this.size
      }
      return this.btnSize
    }
  },
  mounted() {
    if (this.displayLive) {
      window.addEventListener('rfactor-live-event', this.updateRfactorState)
    }
    this.$eventHub.$emit('requestDeviceUpdate')
    this.$eventHub.$emit('getCurrentGfxPreset')
  },
  created() {
    this.$eventHub.$on('deviceUpdate', this.setDeviceState)
    this.$eventHub.$on('currentGfxPreset', this.setCurrentGfxPreset)
  },
  destroyed() {
    this.$eventHub.$off('deviceUpdate', this.setDeviceState)
    this.$eventHub.$off('currentGfxPreset', this.setCurrentGfxPreset)
    if (this.displayLive) {
      window.removeEventListener('rfactor-live-event', this.updateRfactorState)
    }
  }
}
</script>

<style scoped>

</style>