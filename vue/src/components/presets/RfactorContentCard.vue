<template>
  <b-card class="mt-2 setting-card text-center" header-class="m-0 p-2"
          bg-variant="dark" text-variant="white" :id="groupId" :footer-class="compact ? 'd-none' : ''">
    <template #header v-if="displayText">
      <b-icon v-if="headerIcon" :icon="headerIcon"></b-icon>
      <span :class="headerIcon ? 'ml-2' : ''">{{ displayText }}</span>
      <slot name="header"></slot>
    </template>

    <slot name="content"></slot>

    <!-- Content Selection-->
    <template v-if="content.series.length > 0">
      <div class="setting mr-3 mb-3" v-for="contentType in contentTypes" :key="contentType">
        <b-input-group size="sm" class="setting-field">
          <b-input-group-prepend>
            <b-input-group-text class="info-field fixed-width-name" :id="nameId + contentType">
              {{ contentType.charAt(0).toUpperCase() + contentType.slice(1) }}
            </b-input-group-text>
          </b-input-group-prepend>
          <b-input-group-append>
            <!-- Dropdown Menu -->
            <b-dropdown :text="currentContentName[contentType]" class="setting-item fixed-width-setting no-border"
                        :id="elemId + contentType" :disabled="frozen"
                        :variant="currentContentName[contentType] === 'None' ? 'rf-blue' : 'rf-orange'">
              <b-dropdown-item v-for="item in displayContent[contentType]" :key="item.id"
                               @click="selectItem(contentType, item)">
                {{ item.name }}
              </b-dropdown-item>
            </b-dropdown>
          </b-input-group-append>
        </b-input-group>
      </div>
    </template>
    <template v-if="content.series.length === 0 && !frozen">
      <div class="text-rf-orange">
        <b>rF2 content is unknown. Use the refresh button to acquire rF2 content list.</b>
      </div>
    </template>
    <template v-if="content.series.length === 0 && frozen">
      <div v-for="contentType in contentTypes" :key="contentType"
           class="setting mr-3 mb-3 input-group-text info-field fixed-width-name">
        <template v-if="selected[contentType] !== null">
          {{ contentType.charAt(0).toUpperCase() + contentType.slice(1) }}: {{ selected[contentType] }}
        </template>
      </div>
    </template>

    <template #footer v-if="!compact">
      <slot name="footer"></slot>

      <!-- Refresh Button -->
      <div class="float-left">
        <b-button variant="light" id="content-refresh-button" size="sm">
          <b-icon icon="arrow-clockwise"></b-icon>
        </b-button>
      </div>
    </template>

    <!-- Refresh Popover -->
    <b-popover target="content-refresh-button" triggers="click">
      <p>Do you want to <b>start Le Mans Ultimate</b> and refresh the list of available content?</p>
      <p>The game will be quit once the list of content is acquired. This will take ~8 seconds.</p>
      <div class="text-right">
        <LaunchRfactorBtn @make-toast="makeToast" @launch="refreshContent" text="Refresh" />
        <b-button @click="$root.$emit('bv::hide::popover', 'content-refresh-button')"
                  size="sm" aria-label="Close" class="ml-1">
          Close
        </b-button>
      </div>
    </b-popover>
  </b-card>
</template>

<script>
import {getEelJsonObject, setFixedWidth, clearElementsWidthStyle} from "@/main";
import LaunchRfactorBtn from "@/components/widgets/LaunchRfactorBtn.vue";

export default {
  name: "RfactorContentCard",
  components: {LaunchRfactorBtn},
  props: {text: String, fixedWidth: Boolean, settings: Array, headerIcon: String, frozen: Boolean, compact: Boolean },
  data: function () {
    return {
      groupId: 'contentarea' + this._uid,
      nameId: 'contentname' + this._uid,
      elemId: 'contentdrop' + this._uid,
      content: {'series': [], 'tracks': [], 'location': [], 'layout': [], 'manufacturer': [], 'model': [], 'cars': []},
      contentTypes: ['series', 'location', 'layout', 'manufacturer', 'model', 'cars'],
      staticTypes: ['series', 'tracks', 'location', 'manufacturer'],
      selected: {
        'series': null, 'tracks': null, 'location': null, 'layout': null,
        'manufacturer': null, 'model': null, 'cars': null,
      },
      displayText: 'rF2 Content',
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    selectItem: function (contentType, item) {
      if (contentType === 'manufacturer') { this.selectItem('model', undefined) }
      if (contentType === 'model') { this.selectItem('cars', undefined) }
      if (contentType === 'location') { this.selectItem('layout', undefined) }
      if (contentType === 'layout' && item !== undefined) {
        this.selected['tracks'] = item['track_id']
        console.log('Selected Track', item['name'])
      }

      if (item !== undefined) {
        this.selected[contentType] = item.id
      } else {
        this.selected[contentType] = null
      }
    },
    getCurrentName: function (contentType) {
      let item = this.getItem(contentType, this.selected[contentType])
      if (item !== undefined) { return item.name }
      return 'None'
    },
    getItem: function (contentType, id) {
      let result_item = undefined
      let items = this.getContentItems(contentType)

      items.forEach(item => {
        if (item.id === id) { result_item = item }
      })

      if (result_item === undefined && items.length > 0) {
        if (this.selected[contentType] === null) { this.selected[contentType] = items[0].id }
        if (contentType === 'layout') {
          this.selected['tracks'] = items[0]['track_id']
          console.log('Selected Track for location', items[0]['name'])
        }
        return items[0]
      }

      if (this.selected[contentType] === null) {
        if (result_item !== undefined) { this.selected[contentType] = result_item.id }
      }
      return result_item
    },
    getContentItems: function(contentType) {
      if (this.staticTypes.indexOf(contentType) !== -1) { return this.content[contentType] }
      if (contentType === 'model') {
        let car_model_items = []
        const manufacturer = this.selected['manufacturer']
        this.content['model'].forEach(item => {
          if (item.manufacturer === manufacturer) { car_model_items.push(item) }
        })
        return car_model_items
      }
      if (contentType === 'cars') {
        let cars = []
        const car_model = this.selected['model']
        this.content['cars'].forEach(item => {
          if (item['fullPathTree'] === car_model) { cars.push(item) }
        })
        return cars
      }
      if (contentType === 'layout') {
        let layouts = []
        const location = this.selected['location']
        this.content['layout'].forEach(item => {
          if (item['location'] === location) { layouts.push(item) }
        })
        return layouts
      }
    },
    getContent: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.get_content()())

      if (!r.result) {
        this.$emit('error', r.msg)
        this.setBusy(false)
        return
      }
      this.content = r.content

      this.setBusy(false)
    },
    refreshContent: async function() {
      await window.eel.refresh_content()
      this.$root.$emit('bv::hide::popover', 'content-refresh-button')
      this.$emit('launched')
    },
    startUp: async function () {
      if (this.text !== undefined) { this.displayText = this.text }

      // Update selection from Preset Settings
      this.contentTypes.forEach(contentType => {
        const setting = this.getPresetSetting(contentType)
        if (setting !== undefined) {
          this.selected[contentType] = setting.value
          console.log('Selecting: ', contentType, setting.value)
        }
      })

      // Update Content
      await this.getContent()
    },
    setFixedWidth: function () {
      if (!this.fixedWidth) { return }
      this.contentTypes.forEach(c => {
        setFixedWidth(this.groupId, this.nameId + c, this.elemId + c)
      })
    },
    getPresetSetting: function (contentType) {
      let result = undefined
      this.settings.forEach(setting => { if (setting.key === contentType) { result = setting } })
      return result
    },
    updateSetting: function (contentType, value) {
      if (value === null || value === undefined) { return }
      console.log('Updating Content Selection:', contentType, value, )
      this.$emit('update-setting', this.getPresetSetting(contentType), value)

      this.$nextTick(() => {
        clearElementsWidthStyle(this.groupId)
        this.$nextTick(() => { this.setFixedWidth() })
      })
    },
  },
  watch: {
    'selected.series': { handler(val) { this.updateSetting('series', val) },
      deep: true
    },
    'selected.manufacturer': { handler(val) { this.updateSetting('manufacturer', val) },
      deep: true
    },
    'selected.model': { handler(val) { this.updateSetting('model', val) },
      deep: true
    },
    'selected.cars': { handler(val) { this.updateSetting('cars', val) },
      deep: true
    },
    'selected.tracks': { handler(val) { this.updateSetting('tracks', val) },
      deep: true
    },
    'selected.location': { handler(val) { this.updateSetting('location', val) },
      deep: true
    },
    'selected.layout': { handler(val) { this.updateSetting('layout', val) },
      deep: true
    },
  },
  computed: {
    displayContent: function () {
      let dispContent = {}
      this.contentTypes.forEach(contentType => {
        dispContent[contentType] = this.getContentItems(contentType)
      })
      return dispContent
    },
    currentContentName: function () {
      let nameObj = {}
      this.contentTypes.forEach(contentType => { nameObj[contentType] = this.getCurrentName(contentType) })
      return nameObj
    }
  },
  async created() {
    await this.startUp()
  },
  mounted() {
    // Update fixed width
    // Access after rendering finished
    this.$nextTick(() => { this.setFixedWidth() })
  }
}
</script>

<style scoped>
.text-field { border-radius: 0 !important; }
</style>