<template>
  <div>
    <PresetUi ref="gfxPresetUi"
              :id-ref="idRefName" :display-name="displayName"
              :presets="gfxHandler.presets"
              :previous-preset-name="gfxHandler.previousPresetName"
              :selected-preset-idx="gfxHandler.selectedPresetIdx"
              :preset-dir="gfxHandler.userPresetsDir"
              @save-preset="gfxHandler.savePreset"
              @refresh="gfxHandler.getPresets"
              @update-presets-dir="gfxHandler.setPresetsDir"
              @export-current="gfxHandler.exportPreset"
              @select-preset="gfxHandler.selectPreset"
              @create-preset="gfxHandler.createPreset"
              @delete-preset="gfxHandler.deletePreset"
              @update-setting="gfxHandler.updateSetting"
              @update-desc="gfxHandler.updateDesc"
              @update-view-mode="gfxHandler.updateViewMode"
              @make-toast="makeToast" />

    <div v-for="(gfxPreset, idx) in gfxHandler.presets" :key="gfxPreset.name">
      <GraphicsArea :preset="gfxPreset" :idx="idx" :search="search" :fixed-width="fixedWidth"
                    :current_preset_idx="gfxHandler.selectedPresetIdx"
                    :previous-preset-name="gfxHandler.previousPresetName"
                    :view_mode="gfxHandler.viewMode"
                    @update-setting="updateSetting"
                    @set-busy="setBusy"
                    @make-toast="makeToast" />
    </div>
  </div>
</template>

<script>
import PresetUi from "@/components/presets/PresetUi.vue";
import GraphicsArea from "@/components/pages/GraphicsArea.vue";

export default {
  name: "GraphicsPresetArea",
  data: function () {
    return {
      displayDefaultName: 'Graphics'
    }
  },
  props: {gfxHandler: Object, name: String, idRef: String, search: String, fixedWidth: Boolean},
  components: {PresetUi, GraphicsArea},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateSetting: async function (setting, value, save = true) {
      if (this.$refs.gfxPresetUi !== undefined) {
        this.$refs.gfxPresetUi.triggerRefreshAnimation()
      }
      this.gfxHandler.updateSetting(setting, value, save)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
  },
  computed: {
    displayName: function () {
      if (this.name === undefined) { return this.displayDefaultName }
      return this.name
    },
    idRefName: function () {
      if (this.idRef === undefined) { return 'gfx'}
      return this.idRef
    },
  },
}
</script>

<style scoped>

</style>