<template>
  <div>
      <!-- <input type="file" accept=".mp3" @change="audioUpload"> -->
      <input type="file" @change="audioUpload">
      <button @click="audioSubmit">Submit Audio</button>
      <h1>{{ msg }}</h1>
  </div>
</template>

<script>
import axios from "axios";

export default {
data() {
  return {
    audio: null,
    email: "this gets pushed through when opened",
    msg: "nothing"
  };
},
methods: {
  audioUpload(event) {
    this.audio = event.target.files[0];
  },
  async audioSubmit() {
    const data = {
        audio: this.audio,
    }
    try {
      const response = await axios.post(
        "http://localhost:5000/upload",
        data
      );
      console.log(response.data);
      this.msg = 'hiii';
    } catch (error) {
      console.error(error);
      this.msg = error;
    }
  },
  close() {
      // close code
      // yet to figure out if want to do with hidden button or v-if
  }
},
};
</script>