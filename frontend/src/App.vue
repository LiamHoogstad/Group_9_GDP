<script>
import { ref, computed } from "vue";
import axios from "axios";
import AudioUpload from "./components/AudioUpload.vue";
import AudioFiles from "./components/AudioFiles.vue";

export default {
  name: "App",
  components:{
    AudioUpload,
    AudioFiles,
  },

  setup() {},
};
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style scoped></style>
