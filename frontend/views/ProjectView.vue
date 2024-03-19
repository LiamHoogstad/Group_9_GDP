<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import Slider from "../components/Slider.vue";
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
      )}/10000`, /* The '5000' portion is an audio file offset of 5000 miliseconds (5 seconds) */
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
        <h2 id="project_name">{{ title }}</h2>
      </div>
      <div class="centre">
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
      <div class="right">
        <button id="hamburger">
          <img src="@/assets/Hamburger Menu.svg" />
        </button>
      </div>
    </div>
    <div class="upload-area" style="text-align: center; margin-top: 20px">
      <p>{{ fileName }}</p>
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
    </div>
  </div>
</template>

<style scoped>
#ribbon {
  width: 100%;
  height: fit-content;
  background-color: var(--colour-panel-soft);
  padding: 0.5em 0 0.5em 0;
  text-align: center;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

#ribbon .left {
  padding-left: 0.5em;
  text-align: left;
}

#ribbon .centre {
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 15vw;
}

#ribbon .dropdowns span {
  font-weight: 600;
  margin-right: 0.5em;
  padding: 0 0.25em 0 0.25em;
  border-radius: 0.25em;
  cursor: pointer;
}

#ribbon .dropdowns span:hover {
  background-color: var(--colour-interactable);
}

h2#project_name {
  font-family: "Delta Gothic One";
  margin-left: 0.25em;
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
  padding: 0.75em 1em 0.75em 1em;
  cursor: pointer;
  display: flex;
}

button#hamburger img {
  width: 2em;
  height: 2em;
}

#track_list .track{
  margin: 1em 0 0 1em;
  padding: 1em 1em 1em 2em;
  background-color: var(--colour-interactable);
  border-radius: 5em 0 0 5em;
}
</style>
