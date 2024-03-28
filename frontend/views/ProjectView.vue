<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import Slider from "../components/Slider.vue";
import HamburgerMenu from "../components/HamburgerMenu.vue";
import axios from "axios";

const router = useRouter();
const title = ref(router.currentRoute.value.params.title);
const fileName = ref("");
const audioFile = ref(null);
const audioSrc = ref("");
const audio = new Audio();
const isPlaying = ref(false);
const volume = ref(100);

onMounted(() => {
  fetchAudioFile();
  fetchAudioFilename();
});

watch(volume, (newVolume) => {
  const volumeValue = newVolume / 100;
  if (isFinite(volumeValue)) {
    audio.volume = volumeValue;
  } else {
    console.error("Invalid volume:", newVolume);
  }
});

function updateVolume(event) {
  const newVolume = parseInt(event.target.value, 10);
  if (isFinite(newVolume)) {
    volume.value = newVolume;
    audio.volume = newVolume / 100;
  } else {
    console.error("Invalid volume:", newVolume);
  }
}

function handleFileChange(event) {
  const files = event.target.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.type === "audio/mp3" || file.type === "audio/mpeg") {
      fileName.value = file.name;
      audio.src = URL.createObjectURL(file);
      audioFile.value = file;
    } else {
      alert("Please upload an MP3 file.");
    }
  }
}

function togglePlay() {
  isPlaying.value = !isPlaying.value;
  if (isPlaying.value) {
    audio.play();
  } else {
    audio.pause();
  }
}

audio.addEventListener("ended", () => {
  isPlaying.value = false;
});

const uploadAudioFile = async () => {
  if (!audioFile.value) return;
  const formData = new FormData();
  formData.append("file", audioFile.value);
  formData.append("title", title.value);

  const accessToken = localStorage.getItem("userToken");
  try {
    await axios.post("http://127.0.0.1:5000/uploadAudioToProject", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${accessToken}`,
      },
    });

    fetchAudioFile();
  } catch (error) {
    console.error("Upload Error:", error);
  }
};

const fetchAudioFile = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/getAudio/${userId}/${encodeURIComponent(
        title.value
      )}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
        responseType: "blob",
      }
    );
    audioSrc.value = URL.createObjectURL(response.data);
    audio.src = audioSrc.value;
  } catch (error) {
    console.error("Error fetching audio file:", error);
  }
};
const fetchAudioFilename = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/getAudioFilename/${userId}/${encodeURIComponent(
        title.value
      )}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    fileName.value = response.data.audioFilename;
  } catch (error) {
    console.error("Error fetching audio filename:", error);
    fileName.value = "No audio file in project";
  }
};
</script>

<template>
  <div class="projectPage">
    <div id="ribbon">
      <div class="left">
        <div class="dropdowns">
          <span>file</span>
          <span>edit</span>
          <span>insert</span>
          <span>share</span>
          <span>help</span>
        </div>
        <input type="text" id="project_name"v-bind:title="title" v-model = "title"/>
      </div>
      <div class="right">
        <HamburgerMenu/>
      </div>
      <div class="centre">
        <div id="playbackControls">
          <button id="play_pause" @click="togglePlay">
            <img src="../assets/Play.svg" v-if="!isPlaying" />
            <img src="../assets/Pause.svg" v-else />
          </button>
          <Slider
            :value="volume"
            @input="updateVolume"
            :min="0"
            :max="100"
            id="master_volume"
          />
        </div>
      </div>
    </div>
    <div class="upload-area" style="text-align: center">
      <p style="margin-top: 20px">{{ fileName }}</p>
      <v-btn color="primary" depressed>
        <label for="upload-btn" class="custom-file-upload"> Upload MP3 </label>
        <input
          id="upload-btn"
          type="file"
          @change="handleFileChange"
          style="display: none"
          accept=".mp3,audio/*"
        />
      </v-btn>
      <v-btn color="success" @click="uploadAudioFile">Submit Audio</v-btn>
      <div class="first" style="margin-top: 20px">
        <div class="second">
          <table>
            <tr v-for="range in 3">
              <td class="trackControls">
                <button class="delete" title="Delete Track"><h2>x</h2></button>
                <div class="properties">
                  <textarea placeholder="Enter track name...">track name</textarea>
                  <div class="volume">
                    <Slider/>
                    <button title="Solo Track">S</button>
                    <button title="Mute Track">M</button>
                  </div>
                </div>
                <button class="record" title="Record"><h2>•</h2></button>
              </td>
              <td class="trackPreview">QWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIOPASDFGHJKLZXCVBNM</td>
            </tr>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.upload-area {
  contain:size;
}

table {
  border-spacing: 0 0.5em;
}
tr {
  margin: 0px;
  background-color: var(--colour-panel-soft);
  text-align: left;
  height: 6em;
}
td {
  margin: 0px;
  white-space:nowrap;
}

div.second {
    overflow-x:auto;  
    margin-left: calc(25% + 0.5em); 
    overflow-y:auto;
    height: auto;
}
div.first {
    width: auto;
    overflow-y: auto;
    overflow-x: hidden;
    left:0;
    top:auto;
}

.trackControls {
  position: absolute;
  width: 25%;
  height: inherit;
  left: 0.5em;
  top: auto;
  display: flex;
  background-color: var(--colour-panel-hard);
  border-radius: 3em 0 0 3em;
  overflow: hidden;
  box-shadow: 0 0 0.5em var(--colour-dropshadow);
}

.trackControls button.delete {
  background-color: transparent;
  font-family: "Fredoka";
}

.trackControls .properties {
  margin: 0.5em 0.5em 0 0;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.trackControls .properties textarea {
  resize: none;
  background-color: var(--colour-background);
  color: var(--colour-text);
  padding-left: 0.5em;
  overflow: hidden;
  border-radius: 0.25em;
}

.trackControls .properties .volume {
  margin-top: 0.5em;
  height: 1.2em;
  display: flex;
  align-items: center;
}

.trackControls .properties input.slider {
  flex-grow: 1;
}

.trackControls .properties button {
  height: inherit;
  padding: 0;
  margin-left: 0.5em;
  width: 1.2em;
  line-height: 0.3em;
  font-weight: 600;
  background-color: var(--colour-background);
  color: var(--colour-interactable);
}

.trackControls button.record {
  margin: 0.5em 0.5em 0.5em 0;
  padding: 0 0.5em 0 0.5em;
  background-color: var(--colour-background);
  color: var(--colour-interactable);
  font-family: "Fredoka";
}

tr .trackPreview {
  padding: 0 1em 0 1em;
}

#ribbon {
  width: 100%;
  position: sticky;
  contain: layout;
  background-color: var(--colour-panel-soft);
  padding: 0.5em 0 0 0;
}

#ribbon .left {
  width: 33.3333%;
  text-align: left;
  float: left;
  overflow: hidden;
}

#ribbon .right {
  width: 33.3333%;
  text-align: right;
  float: right;
}

#ribbon .centre {
  width: 33.333%;
  float: left;
}

#ribbon .dropdowns span {
  font-weight: 600;
  margin-left: 0.5em;
  padding: 0 0.25em 0 0.25em;
  border-radius: 0.25em;
  cursor: pointer;
}

#ribbon .dropdowns span:hover {
  background-color: var(--colour-interactable);
}

input#project_name {
  font-family: "Delta Gothic One";
  width: 97%;
  font-size: 20pt;
  margin: 0.1em 0 0 0.5em;
  padding-bottom: 0.25em;
  height: 1.1em;
  background-color: transparent;
  color: var(--colour-text);
  border-radius: 0.25em;
  overflow: hidden;
}

input#project_name:focus {
  outline: none;
  border-color: none;
  background-color: var(--colour-panel-hard);
}

#playbackControls {
  display: flex;
  flex-direction: column;
  justify-content: center;
  width:15vw;
  margin: 0 auto 0.5em auto;
}

button {
  color: var(--colour-background);
  background-color: var(--colour-interactable);
  border-radius: 0.25em;
  padding: 0.25em 1em 0.25em 1em;
  font-weight: bold;
  border: none;
}
button:hover {
  background-color: var(--colour-interactable-hover);
}
button:active {
  background-color: var(--colour-interactable-click);
}

button#play_pause {
  margin-bottom: 0.5em;
  cursor: pointer;
}

button#play_pause img {
  width: 1em;
  height: 1em;
}

button#hamburger {
  border-radius: 100% 0 0 100%;
  margin: 0 0 0 auto;
  padding: 0.75em 1em 0.75em 1em;
  cursor: pointer;
  display: flex;
}

button#hamburger img {
  width: 2em;
  height: 2em;
}

#drawer {
  position: absolute;
  overflow: hidden;
  top: 0;
  right: 0;
  width: 0;
  height: 100vh;
  border-radius: 2em 0 0 2em;
  color: var(--colour-background);
  background: var(--colour-interactable);
  font-family: "Delta Gothic One";
  transition: all 0.2s;
}

#drawer ul {
  list-style: none;
  text-align: center;
  margin-top: 0.75em;
}

#drawer a:link,
#drawer a:visited,
#drawer a:active {
  color: var(--colour-background);
  text-decoration: none;
  margin-bottom: 0.25em;
  width: fit-content;
}

#drawer button {
  box-shadow: none;
}

#drawer button.close {
  font-family: "Fredoka";
  font-size: 2.5em;
  min-width: 0;
  padding: 0 .5em 0 0.5em;
}

#drawer button.close:hover {
  background: none;
}
#drawer button.close:active {
  background: none;
}

.v-btn {
  margin: .4em .5em 0 .5em;
}

#track_list .track{
  margin: 1em 0 0 1em;
  padding: 1em 1em 1em 2em;
  background-color: var(--colour-interactable);
  border-radius: 5em 0 0 5em;
}
</style>
