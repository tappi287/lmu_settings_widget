<template>
  <div class="setting" v-if="!settingHidden">
    <b-input-group size="sm" class="setting-field">
      <b-input-group-prepend class="low-round-left">
        <b-input-group-text
            :class="infoFieldClass" :id="nameId">
          {{ setting.name }}
          <b-icon v-if="settingDesc !== ''" icon="info-square" class="ml-2 mr-1"
                  v-b-popover.hover.topright="settingDesc">
          </b-icon>
          <b-icon v-if="settingDiff" class="ml-2 mr-1" icon="exclamation-triangle-fill"
                  v-b-popover.hover.topright="settingDifferenceMessage">
          </b-icon>
        </b-input-group-text>
      </b-input-group-prepend>
      <b-input-group-append class="low-round-right">
        <!-- Dropdown Menu -->
        <template v-if="inputType === 'value'">
          <b-dropdown :text="currentSettingName" :variant="variant" :id="elemId" size="sm"
                      toggle-class="settings-dropdown low-round-right"
                      class="setting-item fixed-width-setting no-border" :disabled="disabled">
            <b-dropdown-item v-for="s in setting.settings" :key="s.value" class="setting-dropdown-item"
                             @click="selectSetting(s)">
              {{ s.name }}
              <b-icon v-if="s.desc !== undefined" icon="info-square"
                      class="ml-2" v-b-popover.hover.topright="s.desc">
              </b-icon>
              <b-icon v-if="showPerformance && s.perf !== undefined" icon="bar-chart"
                      class="ml-2 text-muted"
                      v-b-popover.hover.topright="s.perf.replace('G', 'GPU').replace('C', 'CPU')">
              </b-icon>
            </b-dropdown-item>
          </b-dropdown>
        </template>
        <!-- Spinner Menu -->
        <template v-if="inputType === 'range'">
          <div :id="elemId" class="fixed-width-setting position-relative">
            <b-form-spinbutton v-model="rangeValue" :min="rangeMin" :max="rangeMax" :step="rangeStep"
                               size="sm" inline
                               :class="'spinner-setting rounded-0 low-round-right btn-' + variant"
                               :disabled="disabled"
                               @change="spinnerSettingUpdated" :formatter-fn="spinnerDisplay">
            </b-form-spinbutton>
          </div>
          <b-popover ref="spinnerPopover" :target="elemId" :triggers="'manual'">
            <template #title>Manual Input</template>
            <template #default>
              <div role="group">
                <label :for="'input-' + elemId">
                  Manually enter a value between {{ rangeMin }} and {{ rangeMax }}:
                </label>
                <b-form-input
                    :id="'input-' + elemId" size="sm" debounce="100" :disabled="disabled"
                    v-model="spinnerInputValue" type="number"
                    :max="rangeMax" :min="rangeMin" :step="rangeStep"
                    :state="spinnerInputState" number />
                <b-form-invalid-feedback :id="'input-' + elemId + '-feedback'">
                  Enter a value within the described range and use a dot . as decimal separator.
                </b-form-invalid-feedback>
              </div>
              <div class="text-right mt-2">
                <b-button @click="confirmSpinnerPopover" :disabled="disabled"
                          size="sm" variant="success" aria-label="Confirm">
                  Confirm
                </b-button>
                <b-button @click="closeSpinnerPopover" size="sm" aria-label="Close" class="ml-1">
                  Abort
                </b-button>
              </div>
            </template>
          </b-popover>
        </template>
      </b-input-group-append>
    </b-input-group>
  </div>
</template>

<script>

import {minutesToDaytime, setFixedWidth} from "@/main";

export default {
  name: 'SettingItem',
  data: function () {
    return {
      currentSettingValue: {},
      elemId: 'setting' + this._uid, // _uid is a unique identifier for each vue component
      nameId: 'name' + this._uid,
      settingDesc: '',
      inputType: 'value',
      rangeMin: 0,
      rangeMax: 1,
      rangeStep: 1,
      rangeDisp: undefined,
      rangeValue: 0,
      spinnerTimeout: null,
      showSpinnerInputPopover: false,
      spinnerInputValue: 0,
      spinnerDebounceRate: 2000,
    }
  },
  props: {
    setting: Object, variant: String, fixedWidth: Boolean, show_performance: Boolean,
    disabled: Boolean, groupId: String, previousPresetName: String
  },
  methods: {
    selectSetting: function (s) {
      this.currentSettingValue = s.value
      console.log('Emitting setting update', this.setting.key, s.value)
      this.$emit('setting-changed', this.setting, s.value)
    },
    spinnerSettingUpdated: function () {
      clearTimeout(this.spinnerTimeout)
      this.spinnerTimeout = setTimeout(this.spinnerDebouncedUpdate, this.spinnerDebounceRate)
      this.currentSettingValue = this.rangeValue
    },
    spinnerDebouncedUpdate: function () {
      this.spinnerTimeout = null
      this.$emit('setting-changed', this.setting, this.rangeValue)
    },
    spinnerDisplay: function (value) {
      if (this.rangeDisp === 'floatdecimal') { return String(value.toFixed(2)) }
      if (this.rangeDisp === 'floatpercent') { return String(Math.round(value * 100)) + '%' }
      if (this.rangeDisp === 'time') { return minutesToDaytime(value) }
      if (this.rangeDisp === 'position') { if (value === 0) { return 'Random' } }
      return value
    },
    iterateSettings: function (func) {
      if (this.setting === undefined) { return }
      for (let i=0; i <= this.setting.settings.length; i++) {
        let setting = this.setting.settings[i]
        if (setting === undefined) { continue }
        func(this, setting)
      }
    },
    setupSpinnerDblClick: function () {
      // Double clicking the output/value will open a manual input Popover
      let output = document.getElementById(this.elemId).querySelector('output')
      output.addEventListener('dblclick', this.handleSpinnerDblClick, false)
    },
    handleSpinnerDblClick: function () {
      this.spinnerInputValue = this.rangeValue
      this.$refs.spinnerPopover.$emit('open')
    },
    confirmSpinnerPopover: function () {
      this.closeSpinnerPopover()
      if (this.checkSpinnerInputValue(this.spinnerInputValue)) {
        this.rangeValue = this.spinnerInputValue
        this.spinnerSettingUpdated()
        console.log('Confirmed spinner manual input value', this.spinnerInputValue)
      }
    },
    closeSpinnerPopover: function () { this.$refs.spinnerPopover.$emit('close') },
    checkSpinnerInputValue: function (value) {
      if (Number.isFinite(value)) {
        if (value >= this.rangeMin && value <= this.rangeMax) {
          return true
        }
      }
      return false
    },
    setFixedWidth: function () {
      if (this.fixedWidth) {
        setFixedWidth(this.groupId, this.nameId, this.elemId)
      }
    },
  },
  created: function () {
    // Set description
    this.settingDesc = this.setting.desc || ''

    // Check Setting Type
    if (this.setting.settings !== undefined && this.setting.settings.length) {
      if (this.setting.settings[0].settingType !== undefined) {
        if (this.setting.settings[0].settingType === 'range') {
          this.inputType = 'range'
          this.rangeMin = this.setting.settings[0].min
          this.rangeMax = this.setting.settings[0].max
          this.rangeStep = this.setting.settings[0].step
          this.rangeDisp = this.setting.settings[0].display
          this.rangeValue = this.setting.value
          this.spinnerInputValue = this.setting.value
          this.settingDesc = this.setting.desc || this.setting.settings[0].desc || ''
          this.$nextTick(() => { this.setupSpinnerDblClick() })
        }
      }
    }
  },
  mounted () {
    // if (this.variant === undefined) { this.variant = 'secondary'}
    this.currentSettingValue = this.setting.value
    // Access after rendering finished
    this.$nextTick(() => {
      this.setFixedWidth()
    })
    this.$emit('setting-ready', this)
  },
  computed: {
    currentSettingName: function () {
      let name = 'Not Set!'
      if (this.setting === undefined) { return name }
      this.iterateSettings(function (instance, setting) {
        if (instance.currentSettingValue === setting.value) {
          name = setting.name
        }
      })
      return name
    },
    infoFieldClass: function () {
      if (this.settingDiff) { return 'info-field diff low-round-left fixed-width-name' }
      return 'info-field low-round-left fixed-width-name'
    },
    showPerformance: function () {
      if (this.show_performance !== undefined) { return this.show_performance }
      return false
    },
    settingHidden: function () {
      if (this.setting === undefined) { return true }
      return this.setting['hidden'] || false
    },
    settingDiff: function () {
      if (this.previousPresetName === '' || this.setting === undefined) { return false }
      return this.setting.difference
    },
    settingDifferenceMessage: function () {
      let name = this.setting.difference_value
      this.iterateSettings(function (instance, setting) {
        if (instance.setting.difference_value === setting.value) {
          name = setting.name
        }
      })
      return 'Deviating value in Preset "' + this.previousPresetName + '": ' + name
    },
    spinnerInputState: function () {
      return this.checkSpinnerInputValue(this.spinnerInputValue)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
<style>
.spinner-setting { width: 100% !important; }
.spinner-overlay {
  width: 50%;
  height: 75%;
  position: absolute;
  left: 22.5%;
  margin: .25rem;
}
</style>
