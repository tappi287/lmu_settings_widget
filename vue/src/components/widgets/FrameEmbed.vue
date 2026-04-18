<template>
  <div class="frame-embed-container position-relative" v-cloak>
    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading-container">
      <b-spinner />
    </div>
    
    <!-- iFrame Container -->
    <div 
      v-show="!isLoading" 
      class="position-relative iframe-wrapper" 
      :style="{ height: height }"
    >
      <iframe
        ref="portalFrame"
        :src="url"
        class="w-100 h-100"
        style="border: none; background: transparent;"
        allowtransparency="true"
        @load="onIframeLoad"
        @error="onIframeError"
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
      ></iframe>
    </div>
  </div>
</template>

<script>
export default {
  name: "FrameEmbed",
  props: {
    url: {
      type: String,
      required: true
    },
    height: {
      type: String,
      default: "calc(100vh - 160px)"
    }
  },
  data: function () {
    return {
      isLoading: true,
      loadTimer: null
    }
  },
  mounted: function () {
    this.start()
  },
  beforeUnmount: function () {
    if (this.loadTimer) {
      clearTimeout(this.loadTimer)
    }
  },
  methods: {
    onIframeLoad: function () {
      this.setLoaded()
    },
    onIframeError: function () {
      this.isLoading = false
    },
    start: function () {
      this.isLoading = true

      // Native load listener as fallback
      const iframe = this.$refs.portalFrame
      if (iframe) {
        iframe.addEventListener('load', this.setLoaded, { once: true })
      }

      // Timeout fallback - hide loader after 2 seconds regardless of load state
      this.loadTimer = setTimeout(() => {
        if (this.isLoading) {
          this.isLoading = false
        }
      }, 2000)
    },
    setLoaded: function () {
      if (this.loadTimer) {
        clearTimeout(this.loadTimer)
        this.loadTimer = null
      }
      this.isLoading = false
    }
  }
}
</script>

<style scoped>
.frame-embed-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 120px);
  color: #666;
}

.iframe-wrapper {
  width: 100%;
}
</style>
