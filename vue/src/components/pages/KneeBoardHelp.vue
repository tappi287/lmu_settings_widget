<script lang="ts">
import {defineComponent} from 'vue'

export default defineComponent({
name: "KneeBoardHelp"
})
</script>

<template>
  <b-container class="text-left" fluid>
    <b-card class="mt-2 p-2 setting-card rounded" header-class="m-0 p-2" bg-variant="dark" text-variant="white">
      <template #header>
          <h3 class="float-left mr-1">
            <b-icon icon="clipboard" class="mr-2"></b-icon>KneeBoard
          </h3>
          <b-button variant="transparent" @click="$emit('close')" class="pr-0 pt-0 text-white float-right">
            <b-icon icon="x-circle-fill"></b-icon>
          </b-button>
      </template>

      <!-- Description -->
      <b-card-text>
        This is a display widget meant to be displayed in OpenKneeBoard in Virtual Reality or on a separate Screen
        in Pancake mode. You can display performance metrics to easier fine-tune your future Settings while on track.
      </b-card-text>

      <!-- Actions -->
      <b-card-text>
        <b-row class="mt-5">
          <b-col><h4>OpenKneeboard</h4></b-col>
          <b-col><h4>PresentMon</h4></b-col>
        </b-row>
        <b-row>
          <b-col><p>Capture and display this window in Virtual Reality.</p></b-col>
          <b-col><p>Measure frame time and GPU rendertimes to determine if you're System or GPU bound in certain scenarios.</p></b-col>
        </b-row>
        <b-row>
          <b-col>
            <ol>
              <li>Install <b-link target="_blank" href="https://go.openkneeboard.com/download">OpenKneeboard</b-link></li>
              <li>Go to <b class="text-white-50">Settings > Tabs > Add a Tab > Window Capture</b></li>
              <li>
                Under <i class="text-white-50">Match window title</i> select <i class="text-white-50">Match with pattern</i> and enter:
                <pre class="text-white-50">LMU Settings Widget v?.?.?</pre></li>
            </ol>
          </b-col>
          <b-col>
            <ol>
              <li>Install <b-link target="_blank" href="https://game.intel.com/us/intel-presentmon/">Intel® PresentMon</b-link></li>
              <li>Reboot or make sure PresentMonService is running as a Windows Service</li>
            </ol>
          </b-col>
        </b-row>
        <!-- Desc -->
        <b-row>
          <b-col><span>This will capture this Webbrowser window. You can put this window into fullscreen mode with F11.</span></b-col>
          <b-col>
            <span>This will install the PresentMon Service which is used to capture performance metrics.
            <b>You do not need</b> to start the Intel PresentMon Overlay Application.
              Installing the PresentMon package should have installed and started the PresentMon windows service.
            </span>
          </b-col>
        </b-row>

        <!-- App Settings -->
        <b-row class="mt-4">
          <b-col>
            <h4>Preferences</h4>
            <span>
              Navigate to the <b-icon icon="gear-fill" /> Preferences Page to disable or enable Hardware and
              Performance metric capturing. The performance impact of capturing should not be noticeable at all.
              But of course you can decide to switch it off completely in the application preferences.
            </span>
          </b-col>
        </b-row>
      </b-card-text>
      <b-card-footer class="text-right p-0">
        <b-button variant="dark" @click="$emit('close')">Close</b-button>
      </b-card-footer>
    </b-card>
  </b-container>
</template>

<style scoped>

</style>