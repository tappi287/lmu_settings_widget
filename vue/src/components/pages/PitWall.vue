<template>
  <div class="pit-wall-page">
    <FrameEmbed 
      url="http://localhost:9000" 
      height="calc(100vh - 160px)" 
    />
  </div>
</template>

<script>
import FrameEmbed from "@/components/widgets/FrameEmbed.vue";

export default {
  name: "PitWall",
  components: {
    FrameEmbed
  }
}
</script>

<style scoped>
.pit-wall-page {
  height: 100%;
  width: 100%;
}
</style>
