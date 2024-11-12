<template>
  <div id="rf-overlay" :class="this.showBackdrop ? 'minimized-overlay' : 'center-overlay'">
    <div id="rf-overlay-centered" :class="this.showBackdrop ? 'rf-overlay-centered-center' : 'rf-overlay-centered-center'">
      <div :class="this.showBackdrop ? 'pb-2' : 'busy-div p-4 rounded'"
           id="rf-overlay-content">
        <template v-if="!live">
          <div class="d-flex justify-content-center mb-3">
            <b-spinner label="Loading..."></b-spinner>
          </div>
        </template>
        <template v-else>
          <div class="d-flex justify-content-center">
            <b-button variant="secondary" :size="showBackdrop ? 'sm' : 'md'"
                      @click="setBusy(false);proceed()"
                      v-b-popover.top.hover="'Click to toggle this overlay. ' +
                       'If you started to watch a replay with this app: ' +
                       'Please wait a moment so the app can restore the original video settings. ' +
                       'Detecting LMU not running can take up to a minute.'">
              <b-icon :icon="this.showBackdrop ? 'arrow-up-right' : 'arrow-down-left'" />
              Back
            </b-button>
            <b-button class="ml-2" variant="danger" id="quit-rfactor" :size="showBackdrop ? 'sm' : 'md'">
              Quit Le Mans Ultimate
            </b-button>

            <!-- Quit Popover -->
            <b-popover target="quit-rfactor" triggers="click">
              <template #title>Quit Le Mans Ultimate</template>
              <p>Do you really want to request the currently running instance of Le Mans Ultimate to quit?</p>
              <div class="text-right">
                <b-button variant="danger"
                          @click="quitRfactor(); $root.$emit('bv::hide::popover', 'quit-rfactor')">
                  <b-spinner v-if="quitBusy" class="mr-1"></b-spinner>Quit
                </b-button>
                <b-button class="ml-2" variant="secondary"
                          @click="$root.$emit('bv::hide::popover', 'quit-rfactor')">
                  Close
                </b-button>
              </div>
            </b-popover>
          </div>
          <pre class="text-white mt-3" v-if="rf2Status !== ''"><span>{{ rf2Status }}</span></pre>
          <div v-if="!showBackdrop" class="mt-3">Le Mans Ultimate is currently running.</div>
        </template>
      </div>
    </div>
    <b-overlay no-wrap fixed class="rf-bg-overlay" z-index="1" variant="transparent" blur="1px" :show="!showBackdrop">
      <template #overlay><div><!-- Hide default Spinner --></div></template>
    </b-overlay>
    <!--<div id="rf-spacer" v-if="this.showBackdrop"></div> -->
  </div>
</template>

<script>

export default {
  name: "RfactorOverlay",
  data: function () {
    return { showBackdrop: false }
  },
  props: { rf2Status: String, quitBusy: Boolean, live: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000, noAutoHide = false) {
      this.$emit('make-toast', message, category, title, append, delay, noAutoHide)
    },
    setBusy (busy) { this.$emit('set-busy', busy) },
    proceed () { this.showBackdrop = !this.showBackdrop },
    minimize () { this.showBackdrop = true; },
    quitRfactor () {this.$emit('quit-rfactor') }
  }
}
</script>

<style scoped>
.busy-div { background: rgba(0,0,0, 0.80); }
#rf-overlay {
  width: 100%; height: 100%; top: 0; left: 0; overflow: hidden;
  z-index: 500; pointer-events: none;
}
div#rf-overlay.center-overlay {
  position: fixed;
  pointer-events: none;
}
div#rf-overlay.center-overlay {
  position: fixed;
  pointer-events: none;
}
#rf-overlay.minimized-overlay {
  position: relative;
}
#rf-overlay-centered {
  display: flex;
  min-height: calc(100% - 1.5rem);
  width: auto; max-width: fit-content; pointer-events: none;
  z-index: 10; position: relative;
}
.rf-overlay-centered-side { align-items: self-end; margin: 0 0 0 calc(100% - 25.85rem); transition: all .2s;}
.rf-overlay-centered-center { align-items: center; margin: 0 auto; transition: all .2s;}
#rf-overlay-content { pointer-events: all; width: 25rem; }
#rf-spacer { height: 9.5rem; }
</style>