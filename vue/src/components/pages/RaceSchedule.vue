<template>
  <div id="event-viewer" class="position-relative" v-cloak>
    <FrameEmbed 
      :url="url" 
    />
  </div>
</template>

<script>
import FrameEmbed from "@/components/widgets/FrameEmbed.vue";
import lmwLogoUrl from "@/assets/lmw_logo.png";

export default {
  name: "RaceSchedule",
  components: {
    FrameEmbed
  },
  data: function () {
    return {
      logoUrl: lmwLogoUrl,
      url: "https://bot.ilikeviecher.com/event_viewer",
    }
  }
}
</script>

<style scoped>
#event-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
