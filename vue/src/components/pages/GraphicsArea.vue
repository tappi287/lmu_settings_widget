<template>
<div v-if="current_preset_idx === idx">
  <!-- Video Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="video_settings" v-if="showVideoSettings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show-performance="showPerformance"
                :search="search" header-icon="film"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <!--
      <div class="float-left">
        <template v-if="preset.resolution_settings.options[0].value !== null">
          <div v-b-popover.auto.hover="'Screen Resolution, Window Mode and Refresh Rate have been saved and ' +
               'will be applied with this Graphics Preset.'"
               class="h3 mt-0 mb-0 video-indicator">
            <b-iconstack>
              <b-icon stacked shift-v="0.0" icon="display" variant="white" />
              <b-icon stacked shift-v="0.85" icon="check" variant="success" />
            </b-iconstack>
          </div>
        </template>
        <template v-else>
          <div v-b-popover.auto.hover="'Click the Video Setup button to save and apply Screen Resolution, Window Mode ' +
               'and Refresh Rate with this Graphics Preset.'"
                class="h3 mt-0 mb-0 video-indicator">
            <b-icon icon="display-fill" variant="secondary" />
          </div>
        </template>
      </div>
      -->
    </template>
  </SettingsCard>

  <!-- Display Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="graphic_options"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show-performance="showPerformance"
                :view_mode="viewMode"
                :search="search" header-icon="display"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div class="float-right">
        <b-button size="sm" @click="showPerformance = !showPerformance" variant="rf-scondary"
                  v-b-popover.lefttop.hover="'Show performance data next to supported settings in ' +
                   'the dropdown menu. ' +
                   'G=relative GPU performance impact | C=relative CPU performance impact'">
          <b-icon :icon="showPerformance ? 'bar-chart-line-fill' : 'bar-chart-line'"></b-icon>
        </b-button>
      </div>
    </template>
  </SettingsCard>

  <!-- View Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="graphic_view_options"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show-performance="showPerformance"
                :view_mode="viewMode"
                :search="search" header-icon="person-square"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- Advanced Display Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="advanced_graphic_options"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show_performance="showPerformance"
                :view_mode="viewMode"
                :search="search" header-icon="card-list"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- VRToolKit Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="reshade_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #header>
      <b-alert class="mt-4 small" variant="info" :show="showOpenXrHint">
        Detected non-original OpenVR binary [openvr_api.dll] in your installation.
        If you use OpenComposite / OpenXR: make sure to set <b>Use OpenXR</b> to enabled!
      </b-alert>
      <b-alert class="mt-4 small" variant="warning" :show="showOpenVrHint">
        Warning: detected native OpenVR in your installation. Injecting ReShade vie OpenXR will not work
        for this game because it will not use OpenXR. Set <b>Use OpenXR</b> to disabled!
      </b-alert>
    </template>
    <template #footer v-if="!compact">
      <div style="font-size: small;">
        Visit
        <b-link class="text-rf-orange" target="_blank" href="https://vrtoolkit.retrolux.de/">
          vrtoolkit.retrolux.de
        </b-link>
        for more information.
        <br /><br />
        If you want to adjust settings in-game: create a new preset inside the ReShade UI.
        The settings you adjust here will use a custom Reshade preset "lmu_widget_preset.ini".
        <br />
        To use these enhancements in PanCake mode: set the <i>"Use Center Mask"</i> setting to <i>Disabled</i>
        <div class="float-right">
          <b-button size="sm" @click="showAllReshade = !showAllReshade" variant="rf-secondary"
                    v-b-popover.lefttop.hover="'Show all VRToolKit setting details even if they are not activated.'">
            <b-icon :icon="showAllReshade ? 'chevron-double-up' : 'chevron-double-down'"></b-icon>
          </b-button>
        </div>
      </div>
    </template>
  </SettingsCard>
  <!-- ReShade FAS Settings -->
  <SettingsCard v-if="sharpeningFas"
                :preset="preset" :idx="idx" settings-key="reshade_fas_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade CAS Settings -->
  <SettingsCard v-if="sharpeningCas"
                :preset="preset" :idx="idx" settings-key="reshade_cas_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade LUT Settings -->
  <SettingsCard v-if="applyLUT"
                :preset="preset" :idx="idx" settings-key="reshade_lut_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade CC Settings -->
  <SettingsCard v-if="colorCorrection"
                :preset="preset" :idx="idx" settings-key="reshade_cc_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade AA Settings -->
  <SettingsCard v-if="antiAliasing"
                :preset="preset" :idx="idx" settings-key="reshade_aa_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- ReShade Clarity2.fx PreProcessor Definitions -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="reshade_clarity_fx_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="claritySettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled && clarityEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade Clarity2.fx Options -->
  <SettingsCard v-if="clarity"
                :preset="preset" :idx="idx" settings-key="reshade_clarity_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="claritySettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled && clarityEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
</div>
</template>

<script>
import SettingsCard from "@/components/settings/SettingsCard.vue";
import {getEelJsonObject} from "@/main.js";

export default {
  name: "GraphicsArea",
  data: function () {
    return {
      showPerformance: true, showAllReshade: false,
      abortResolutionUpdate: false, showOpenVrSettings: true, showVideoSettings: true,
      originalOpenVRPresent: false,
    }
  },
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number, search: String,
          previousPresetName: String, fixedWidth: Boolean, compact: Boolean, frozen: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateSetting: function (setting, value) {
      this.$emit('update-setting', setting, value)
    },
    setBusy: function (busy) { this.$emit('set-busy', busy) },
    _getSetSettingsOption(settings_key, option_key, setValue=null) {
      let result = null
      this.preset[settings_key].options.forEach(o => {
        if (o.key === option_key) {
          if (setValue !== null) { o.value = setValue }
          result = o.value
        }
      })
      return result
    },
    async checkOriginalOpenVRPresent () {
      const r = await getEelJsonObject(window.eel.is_original_openvr_present()())
      if (r.result !== undefined) {
        this.originalOpenVRPresent = r.result
      }
    },
    reshadeSettingDisabled(setting) {
      if (setting.key === 'use_reshade') { return false }
      return !this.reshadeEnabled
    },
    claritySettingDisabled(setting) {
      if (setting.key === 'use_clarity') { return false }
      return !this.clarityEnabled
    }
  },
  components: {
      SettingsCard
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    },
    showOpenVrHint: function () {
      if (this.preset === undefined) { return false }

      if (this.reshadeEnabled && this.originalOpenVRPresent) {
        if (this._getSetSettingsOption('reshade_settings', 'use_openxr')) {
          return true
        }
      }
      return false
    },
    showOpenXrHint: function () {
      if (this.preset === undefined) { return false }

      if (this.reshadeEnabled) {
        if (!this._getSetSettingsOption('reshade_settings', 'use_openxr')) {
          if (!this.originalOpenVRPresent) {
            return true
          }
        }
      }
      return false
    },
    reshadeEnabled: function () {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('reshade_settings', 'use_reshade')
    },
    clarityEnabled: function () {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('reshade_clarity_fx_settings', 'use_clarity')
    },
    // Display Reshade Setting Details if setting active
    sharpeningFas: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_SHARPENING_MODE') === 1;
    },
    sharpeningCas: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_SHARPENING_MODE') === 2;
    },
    applyLUT: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_COLOR_CORRECTION_MODE') === 1;
    },
    colorCorrection: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_COLOR_CORRECTION_MODE') === 2;
    },
    antiAliasing: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_ANTIALIASING_MODE') === 1;
    },
    clarity: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_clarity_fx_settings', 'use_clarity');
    },
  },
  created() {
    // Show detailed VRToolKit settings if there are settings differences
    if (this.previousPresetName !== '') { this.showAllReshade = true }
    this.checkOriginalOpenVRPresent()
  }
}
</script>

<style>
  .video-indicator { line-height: 0.98; }
  /* .reshadeEnabled > div.setting-card { background-color: rgba(234, 234, 234, 0.13) !important; } */
  .reshadeDisabled > div.setting-card { background-color: rgba(56, 56, 56, 0.13) !important; }
</style>