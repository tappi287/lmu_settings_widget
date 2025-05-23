<template>
<div v-if="current_preset_idx === idx">
  <!-- Content Selection -->
  <RfactorContentCard v-if="contentSelection"
                      show-launch text="Content Selection" @launched="$emit('content-launched')"
                      :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                      :settings="contentSettings"
                      :header-icon="headerIcon"
                      @make-toast="makeToast" @set-busy="setBusy" @update-setting="updateSetting">
    <template #header>
      <slot name="header"></slot>
    </template>
    <template #footer>
      <slot name="contentFooter"></slot>
    </template>
  </RfactorContentCard>

  <!-- Generic Settings -->
  <b-card class="mt-2 setting-card" header-class="m-0 p-2" :id="groupId" v-if="!contentSelection"
          bg-variant="dark" text-variant="white" :footer-class="compact ? 'd-none' : ''">
    <!-- Header -->
    <template #header>
        <b-icon v-if="headerIcon" :icon="headerIcon"></b-icon>
        <span :class="headerIcon ? 'ml-2' : ''">{{ preset[settingsKey].title }}</span>
        <slot name="header"></slot>
    </template>
    <!-- Settings -->
    <template v-if="!viewMode">
      <!-- View Mode Grid -->
      <SettingItem v-for="setting in searchedOptions" :key="setting.key"
               :setting="setting" class="mr-3 mb-3" :fixedWidth="fixedWidth" :frozen="frozen"
               :variant="settingDisabledLocal(setting) ? 'rf-secondary': 'rf-orange'"
               :show_performance="showPerformance"
               :disabled="settingDisabledLocal(setting)"
               :group-id="groupId"
               :previous-preset-name="previousPresetName"
               @setting-changed="updateSetting">
      </SettingItem>
    </template>
    <template v-else>
      <!-- View Mode List -->
      <b-list-group class="text-left">
        <b-list-group-item class="bg-transparent" v-for="setting in searchedOptions"
                           :key="setting.key">
          <SettingItem :setting="setting" :fixedWidth="fixedWidth" :frozen="frozen"
                   :variant="settingDisabledLocal(setting) ? 'rf-secondary' : 'rf-orange'"
                   :show_performance="showPerformance"
                   :disabled="settingDisabledLocal(setting)"
                   :group-id="groupId"
                   :previous-preset-name="previousPresetName"
                   @setting-changed="updateSetting">
          </SettingItem>
        </b-list-group-item>
      </b-list-group>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </b-card>
</div>
</template>

<script>
import SettingItem from "@/components/settings/SettingItem.vue"
import RfactorContentCard from "@/components/presets/RfactorContentCard.vue";
/* import {getEelJsonObject} from "@/main"; */

export default {
  name: "SettingsCard",
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number, settingsKey: String,
          settingDisabled: Function, showPerformance: Boolean, search: String, previousPresetName: String,
          fixedWidth: Boolean, contentSelection: Boolean, headerIcon: String,
          compact: Boolean, frozen: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    updateSetting: function (setting, value) {
      this.$emit('update-setting', setting, value)
    },
    settingDisabledLocal: function (setting) {
      if (this.frozen) { return true }
      if (this.settingDisabled !== undefined) {
        return this.settingDisabled(setting)
      }
      return false
    },
    searchSetting: function (setting) {
      if (this.search === '' || this.search === null || this.search === undefined) { return true }
      let name = ''
      if (setting.name !== null && setting.name !== undefined) { name = setting.name.toLowerCase() }
      let desc = ''
      if (setting.desc !== null && setting.desc !== undefined) { desc = setting.desc.toLowerCase() }
      let value = ''
      if (setting.value !== null && setting.value !== undefined) { value = String(setting.value).toLowerCase() }
      const search = this.search.toLowerCase()
      return name.indexOf(search) !== -1 || desc.indexOf(search) !== -1 || value.indexOf(search) !== -1
    },
  },
  components: {
    SettingItem,
    RfactorContentCard
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    },
    groupId: function () {
      return 'setting-area-' + this._uid
    },
    searchedOptions: function () {
      let settings = []
      this.preset[this.settingsKey].options.forEach(setting => {
        let r1 = this.searchSetting(setting)
        let r2 = false

        setting.settings.forEach(s => { r2 = r2 || this.searchSetting(s) })
        if (r1 || r2) { settings.push(setting) }
      })
      return settings
    },
    contentSettings: function () {
      return this.preset[this.settingsKey].options
    }
  },
}
</script>

<style scoped>

</style>