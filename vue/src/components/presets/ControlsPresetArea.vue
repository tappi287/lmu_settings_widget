<template>
  <div>
    <PresetUi ref="conUi" :id-ref="idRef" :display-name="displayName"
              :presets="conHandler.presets"
              :previous-preset-name="conHandler.previousPresetName"
              :selected-preset-idx="conHandler.selectedPresetIdx"
              :preset-dir="conHandler.userPresetsDir"
              @save-preset="conHandler.savePreset"
              @refresh="conHandler.getPresets"
              @update-presets-dir="conHandler.setPresetsDir"
              @export-current="conHandler.exportPreset"
              @select-preset="conHandler.selectPreset"
              @create-preset="conHandler.createPreset"
              @delete-preset="conHandler.deletePreset"
              @update-setting="conHandler.updateSetting"
              @update-desc="conHandler.updateDesc"
              @update-view-mode="conHandler.updateViewMode"
              @make-toast="makeToast" />
    <div>
      <div v-for="(conPreset, idx) in conHandler.presets" :key="conPreset.name">
        <!-- Controller Assignments -->
        <b-card class="mt-2 setting-card" id="hdl-controller-json-area" header-class="p-3"
                bg-variant="dark" text-variant="white" footer-class="pt-0">
          <template #header>
            <div class="position-relative" v-if="false">
              <b-icon icon="lamp" /><span class="ml-2">Controller Assignments</span>
              <div class="position-absolute headlight-title-right">
                <b-button size="sm" class="rounded-right"
                          v-b-popover.hover.bottom="'Refresh Settings if you updated a setting in-game'">
                  <b-icon icon="arrow-repeat"></b-icon>
                </b-button>
              </div>
            </div>
          </template>
          <ControllerAssignment
              v-for="setting in conPreset.general_controller_assignments.options"
              lmu-assignment
              :key="setting.key"
              :setting="setting"
              variant="rf-orange" class="mr-3 mb-3"
              group-id="controller-assignments-area"
              capture-hint="Press a Controller Device button"
              @update-assignment="updateControllerAssignment"
              @make-toast="makeToast">
          </ControllerAssignment>
        </b-card>
        <!--
        <SettingsCard :preset="conPreset" :idx="idx" :search="search" fixed-width
                      settings-key="freelook_settings" header-icon="card-list"
                      :current_preset_idx="conHandler.selectedPresetIdx"
                      :previous-preset-name="conHandler.previousPresetName"
                      :view_mode="conHandler.viewMode"
                      @update-setting="conHandler.updateSetting"
                      @set-busy="setBusy"
                      @make-toast="makeToast"/>
        <SettingsCard :preset="conPreset" :idx="idx" :search="search" fixed-width
                      settings-key="gamepad_mouse_settings" header-icon="receipt"
                      :current_preset_idx="conHandler.selectedPresetIdx"
                      :previous-preset-name="conHandler.previousPresetName"
                      :view_mode="conHandler.viewMode"
                      @update-setting="conHandler.updateSetting"
                      @set-busy="setBusy"
                      @make-toast="makeToast"/>
        <SettingsCard :preset="conPreset" :idx="idx" :search="search" fixed-width
                      settings-key="general_steering_settings" header-icon="filter-circle"
                      :current_preset_idx="conHandler.selectedPresetIdx"
                      :previous-preset-name="conHandler.previousPresetName"
                      :view_mode="conHandler.viewMode"
                      @update-setting="conHandler.updateSetting"
                      @set-busy="setBusy"
                      @make-toast="makeToast"/>
        -->
      </div>
    </div>
  </div>
</template>

<script>
import PresetUi from "@/components/presets/PresetUi";
import SettingsCard from "@/components/settings/SettingsCard";
import ControllerAssignment from "@/components/settings/ControllerAssignment.vue";
import {getEelJsonObject} from "@/main";

export default {
  name: "ControlsPresetArea",
  data: function () {
    return {
      displayDefaultName: 'Controls',
      lmuToPyGameDeviceMap: {},
    }
  },
  props: {conHandler: Object, idRef: String, name: String, search: String, fixedWidth: Boolean},
  components: {ControllerAssignment, PresetUi, SettingsCard},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
    receiveControllerDeviceEvent (event) {
      console.log(event.detail)
    },
    updateControllerAssignment (setting, event) {
      console.log(setting, event)
      let button = -1
      if (event.button !== undefined && event.button !== null) {
        button = event.button
      }
      if (button === -1) {
        this.makeToast("Currently only buttons are supported.", "Controller Assignment")
        return
      }

      if (this.lmuToPyGameDeviceMap[event.guid] !== undefined) {
        const new_value = {"device": this.lmuToPyGameDeviceMap[event.guid], "id": button + 32}
        setting.value = new_value
        this.conHandler.updateSetting(setting, new_value)
      }
    },
  },
  computed: {
    displayName: function () {
      if (this.name === undefined) { return this.displayDefaultName }
      return this.name
    },
  },
  async created() {
    const r = await getEelJsonObject(window.eel.get_lmu_to_pygame_device_map()())
    if (r !== undefined) {
      this.lmuToPyGameDeviceMap = r
    }
  }
}
</script>

<style scoped>

</style>