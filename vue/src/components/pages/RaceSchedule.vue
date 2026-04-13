<template>
  <div id="event-viewer" class="position-relative" v-cloak>
    <!-- Loading Indicator -->
    <div v-if="isLoading" class="loading-container">
      <b-spinner />
    </div>
    
    <!-- Proxy Mode (bypasses X-Frame-Options) -->
    <div v-show="!isLoading" class="position-relative" style="height: calc(100vh - 160px);">
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
import lmwLogoUrl from "@/assets/lmw_logo.png";

export default {
  name: "RaceSchedule",
  data: function () {
    return {
      logoUrl: lmwLogoUrl,
      isLoading: true,
      url: "https://bot.ilikeviecher.com/event_viewer",
      proxyError: null,
      canOpenDirect: true,
      retryCount: 0,
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
      this.proxyError = 'Error loading site ...'
    },
    start: function () {
      this.isLoading = true
      this.proxyError = null
      this.retryCount = 0

      // Native load listener as fallback
      const iframe = this.$refs.portalFrame
      if (iframe) {
        iframe.addEventListener('load', this.setLoaded, { once: true })
      }

      // Timeout fallback - hide loader after max 8 seconds regardless of load state
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
      this.retryCount = 0
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

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 120px);
  color: #666;
}
</style>
