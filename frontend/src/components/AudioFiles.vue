<template>
  <div>
    <ul>
      <li v-for="audio in audioFiles" :key="audio.audio_id">
          {{ audio.audio_id }} - <button @click="playAudio(audio.audio_data)">Play</button>
      </li>
    </ul>
  </div>
  <AudioUpload ref="audioUpload"/>
</template>

<script>
import AudioUpload from "./AudioUpload.vue";


export default {
  components:{
    AudioUpload,
  },
  data() {
    return {
      audioFiles: [],
      userId: 1234,
    };
  },
  mounted() {
    this.fetchAudioFiles(this.userId);
  },
  methods: {
    async fetchAudioFiles(userId) {
      try {
        const response = await fetch(`/audio_files/${userId}`);
        const data = await response.json();
        this.audioFiles = data;
      } catch (error) {
        console.error('Error fetching audio files:', error);
      }
    },
    playAudio(audioData) {
      const audio = new Audio();
      audio.src = `data:audio/mpeg;base64,${audioData}`;
      audio.play();
    }
  }
}
</script>
