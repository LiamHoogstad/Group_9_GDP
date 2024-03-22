<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import Slider from "../components/Slider.vue";
import axios from "axios";

const router = useRouter();
const title = ref(router.currentRoute.value.params.title);
const showAddAudioPopup = ref(false);
const audioFiles = ref([]);
const volume = ref(100);
const isPlaying = ref(false);

const audioSrc = ref("");

watch(
  audioFiles,
  async () => {
    console.log("Audio files have changed. Streaming all audio files again...");
    await delay(10000);
    await streamAllAudioFiles();
  },
  { deep: true }
);

const togglePlay = async () => {
  const audioPlayer = document.getElementById("projectAudio");
  if (!audioSrc.value) {
    console.log("Setting audio source...");
    const accessToken = localStorage.getItem("userToken");
    const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
    audioSrc.value = `http://127.0.0.1:5000/streamProjectCombinedAudio/${userId}/${encodeURIComponent(
      title.value
    )}`;
  }

  if (audioPlayer.src !== audioSrc.value) {
    audioPlayer.src = audioSrc.value;
  }

  if (!isPlaying.value) {
    try {
      await audioPlayer.play();
      isPlaying.value = true;
    } catch (error) {
      console.error("Playback failed:", error);
    }
  } else {
    audioPlayer.pause();
    isPlaying.value = false;
  }
};

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

onMounted(async () => {
  await fetchAudioFiles();
  //await streamAllAudioFiles();
});

async function streamAllAudioFiles() {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    console.log("TESTING FARTS");
    const streamUrl = `http://127.0.0.1:5000/streamProjectAudios/${userId}/${encodeURIComponent(
      title.value
    )}`;
    audioSrc.value = streamUrl;
    const audioPlayer = document.getElementById("projectAudio");
    audioPlayer.src = audioSrc.value;
    audioPlayer.load();
    audioPlayer.onloadeddata = () => {};
  } catch (error) {
    console.error("Error streaming combined audio files:", error);
  }
}

const fetchAudioFiles = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/getAudios/${userId}/${encodeURIComponent(
        title.value
      )}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    audioFiles.value = response.data.map((file) => ({
      ...file,
      src: `http://127.0.0.1:5000/streamAudio/${file.audioFileId}`,
    }));
    //await streamAllAudioFiles();
  } catch (error) {
    console.error("Error fetching audio files:", error);
  }
};

function updateVolume(newVolume) {
  const volumeValue = newVolume / 100;
  const audioPlayer = document.getElementById("projectAudio");
  audioPlayer.volume = volumeValue;
}

const addAudioRow = () => {
  audioFiles.value.push({ source: "" });
};

const triggerFileInput = (index) => {
  document.getElementById("file-input-" + index).click();
};

const updateFile = async (index, event) => {
  const file = event.target.files[0];
  if (file) {
    const formData = new FormData();
    formData.append("file", file);
    const accessToken = localStorage.getItem("userToken");
    const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

    try {
      const response = await axios.post(
        `http://127.0.0.1:5000/uploadAudioToProject/${userId}/${encodeURIComponent(
          title.value
        )}/${index}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      console.log(response.data.message);
      await fetchAudioFiles();
    } catch (error) {
      console.error("Error uploading file:", error.response.data);
    }
  }
  //await streamAllAudioFiles();
};

const deleteAudioFile = async (index) => {
  const fileToDelete = audioFiles.value[index];
  if (!fileToDelete || !fileToDelete.audioFileId) {
    console.error("File data is missing.");
    return;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    await axios.delete(
      `http://127.0.0.1:5000/deleteAudio/${userId}/${fileToDelete.audioFileId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    console.log("File deleted successfully");
    audioFiles.value.splice(index, 1); // Remove the file from UI list
    await fetchAudioFiles();
    //await streamAllAudioFiles();
  } catch (error) {
    console.error("Error deleting the file:", error.response.data);
  }
};
</script>

<script>
export default {
  data() {
    return {
      drawerVisible: false,
      audioFiles: [],
    };
  },
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
          <img src="../assets/Pause.svg" v-else /></button
        ><Slider
          :value="volume"
          @update:modelValue="updateVolume"
          :min="0"
          :max="100"
        />

        <audio id="projectAudio" controls style="display: none"></audio>
      </div>
      <div class="right">
        <button id="hamburger" @click="drawerVisible = true">
          <img src="@/assets/Hamburger Menu.svg" />
        </button>
      </div>
    </div>
    <div id="uploadArea">
      <div class="editor">
        <div
          v-for="(audio, index) in audioFiles"
          :key="index"
          class="audio-row"
        >
          <span
            >{{ index + 1 }}. {{ audio.audioFilename || "Choose a file" }}</span
          >
          <input
            type="file"
            :id="'file-input-' + index"
            @change="(event) => updateFile(index, event)"
            accept="audio/*"
            style="display: none"
          />
          <button @click="triggerFileInput(index)">Choose File</button>
          <span v-if="!audio.audioFilename">No file chosen</span>
          <button @click="deleteAudioFile(index)">Delete</button>
        </div>
        <button @click="addAudioRow">Add Audio File</button>
      </div>
    </div>
    <div
      id="drawer"
      :style="{
        width: drawerVisible ? '25em' : '0',
        paddingLeft: drawerVisible ? '10px' : '0',
      }"
    >
      <button class="close" @click="drawerVisible = false">x</button>
      <ul>
        <h1><router-link to="/">Home</router-link></h1>
        <h1><router-link to="/explore">Explore</router-link></h1>
        <h1><router-link to="/profile-page">Account</router-link></h1>
      </ul>
    </div>
  </div>
</template>

<style scoped>
#uploadArea {
  max-width: 600px;
  margin: 20px auto;
}
.editor {
  display: flex;
  flex-direction: column;
}
.audio-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

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
  padding: 0 0.5em 0 0.5em;
}

#drawer button.close:hover {
  background: none;
}
#drawer button.close:active {
  background: none;
}

#track_list .track {
  margin: 1em 0 0 1em;
  padding: 1em 1em 1em 2em;
  background-color: var(--colour-interactable);
  border-radius: 5em 0 0 5em;
}
</style>
