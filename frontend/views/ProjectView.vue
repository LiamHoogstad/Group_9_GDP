<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import Slider from "../components/Slider.vue";
import HamburgerMenu from "../components/HamburgerMenu.vue";
import AudioEditor from "../components/AudioEditor.vue"
import { genres, instruments } from '../assets/globalVariables.js';
import MultipleDropdown from "../components/MultipleDropdown.vue";
import axios from "axios";

const router = useRouter();
const route = useRoute();
const title = ref(router.currentRoute.value.params.title);
const audioFiles = ref([]);
const volume = ref(100);
const isPlaying = ref(false);
const audioSrc = ref("");
const combinedAudioReady = ref(false);
const isLoadingAudio = ref(true);
const trackVolumes = [20,40,60,100];

// onMounted(async () => {
//   // Assuming the project title comes from the route parameters (update accordingly)
//   projectTitle.value = route.params.title;

//   const accessToken = localStorage.getItem("userToken");
//   if (!accessToken) {
//     console.error("No access token found. Redirecting to login...");
//     router.push({ name: "SignIn" });
//     return;
//   }

//   const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

//   // Fetch the project by its title and the user's ID
//   await fetchProjectData(userId, projectTitle.value);
// });

watch(
  audioFiles,
  async (newVal, oldVal) => {
    if (newVal.length > 0 && newVal !== oldVal) {
      console.log(
        "Audio files have changed. Streaming all audio files again..."
      );
      await streamAllAudioFiles();
    }
  },
  { deep: true }
);

const togglePlay = async () => {
  const audioPlayer = document.getElementById("projectAudio");
  if (isLoadingAudio.value) {
    console.log("Audio is still loading...");
    return;
  }

  if (!combinedAudioReady.value) {
    console.log("Combined audio is not ready yet. Trying to prepare it...");
    await streamAllAudioFiles();
  }

  if (audioPlayer.src !== audioSrc.value || !isPlaying.value) {
    if (audioPlayer.src !== audioSrc.value) {
      console.log("Setting new audio source.");
      audioPlayer.src = audioSrc.value;
      audioPlayer.load();
    }

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

async function streamAllAudioFiles() {
  isLoadingAudio.value = true;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    console.log("Combining all audio files in the backend...");
    const response = await axios.get(
      `http://127.0.0.1:5000/streamProjectAudios/${userId}/${encodeURIComponent(
        title.value
      )}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    console.log("Audio files combined successfully: ");

    const combinedAudioUrl = `http://127.0.0.1:5000/streamProjectCombinedAudio/${userId}/${encodeURIComponent(
      title.value
    )}`;
    audioSrc.value = combinedAudioUrl + "?v=" + new Date().getTime(); // Adding a timestamp to prevent caching

    await new Promise((resolve, reject) => {
      const audioPlayer = document.getElementById("projectAudio");
      audioPlayer.src = audioSrc.value; // Use the updated src with the timestamp

      audioPlayer.onloadeddata = () => {
        console.log("Audio data has loaded and is now ready to play");
        isLoadingAudio.value = false;
        resolve();
      };

      audioPlayer.onerror = () => {
        console.error("Error loading combined audio");
        reject("Error loading audio");
      };

      audioPlayer.load();
    });

    combinedAudioReady.value = true;
  } catch (error) {
    console.error("Error combining or streaming audio files:", error);
  }
}

async function fetchAudioFiles() {
  isLoadingAudio.value = true;
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/getAudios/${userId}/${encodeURIComponent(title.value)}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    if (!response.data.length) {
      console.log("No audio files were found for this user.");
      audioFiles.value = [];
      trackVolumes.value = [];
    } else {
      audioFiles.value = response.data.map((file) => ({
        ...file,
        src: `http://127.0.0.1:5000/streamAudio/${file.audioFileId}`,
      }));

      trackVolumes.value = response.data.map((file) => file.Volumes);

      console.log("Audio files have been fetched and processed");
      console.log(JSON.stringify(audioFiles,null,2));
      console.log("Track Volumes:", trackVolumes.value);
      console.log("Track Volume 3:", trackVolumes.value[2]);

    }
  } catch (error) {
    console.error("Error fetching audio files:", error);
  } finally {
    // Ensure isLoadingAudio is set to false when the operation is complete
    isLoadingAudio.value = false;
  }
}

/* async function fetchAudioFiles() {
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

    if (!response.data.length) {
      console.log("No audio files were found for this user.");
      // Optionally, clear or set default values if no data is found
      audioFiles.value = [];
      trackVolumes.value = [];

    } else {

      audioFiles.value = response.data.map((file) => ({
      ...file,
      src: `http://127.0.0.1:5000/streamAudio/${file.audioFileId}`,
      }));

      trackVolumes.value = response.data.map((file) => file.Volumes);

      console.log("Audio files have been fetched and processed");
      console.log(JSON.stringify(audioFiles,null,2));
      console.log("Track Volumes:", trackVolumes.value);
      console.log("Track Volume 3:", trackVolumes.value[2]);

    }

  } catch (error) {
    console.error("Error fetching audio files:", error);
  }
} */

onMounted(async () => {
  await fetchAudioFiles();
});

function updateVolume(newVolume) {
  const volumeValue = newVolume / 100;
  const audioPlayer = document.getElementById("projectAudio");
  audioPlayer.volume = volumeValue;
}





/* qweoifnqwpeiofubqweifubqweofiubqweofiuqbweofiuqbwefoiuqwbefoqiuwefoqwieufbqwef */
async function updateTrackVolume(index, newVolume) {
  isLoadingAudio.value = true;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  const indexString = String(index)
  const volumeString = String(newVolume)

  try {

    console.log("Combining all audio files in the backend...");
    const volumeResponse = await axios.get(
      `http://127.0.0.1:5000/updateAudioVolume/${userId}/${encodeURIComponent(title.value)}/${indexString}/${volumeString}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    
    streamAllAudioFiles();

  } catch (error) {
    console.error("Error combining or streaming audio files:", error);
  }

}

const debouncedUpdateTrackVolume = debounce(updateTrackVolume, 500);
function debounce(func, delay) {
  let debounceTimer;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => func.apply(context, args), delay);
  };
}

async function toggleTrackMute(audio, index) {
  isLoadingAudio.value = true;

  audio.Mute = !audio.Mute;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  const indexString = String(index)

  try {

    console.log("Muting File in the backend...");
    const muteResponse = await axios.get(
      `http://127.0.0.1:5000/updateTrackMute/${userId}/${encodeURIComponent(title.value)}/${indexString}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    
    streamAllAudioFiles();

  } catch (error) {
    console.error("Error combining or streaming audio files:", error);
  }

}


async function toggleTrackSolo(audio) {
  audio.Solo = !audio.Solo
}


const addAudioRow = () => {
  audioFiles.value.push({ source: "" });
};

const triggerFileInput = (index) => {
  document.getElementById("file-input-" + index).click();
};
const triggerNewFileInput = () => {
  document.getElementById("new-file-input").click();
};

const updateFile = async (index, event) => {
  const file = event.target.files[0];
  if (file) {
    const formData = new FormData();
    formData.append("file", file);
    const accessToken = localStorage.getItem("userToken");
    const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

    try {
      console.log("Uploading file...");
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
      console.log("Upload response:", response.data.message);

      // Only fetch new audio files list and stream all audio files if the upload was successful
      await fetchAudioFiles();
    } catch (error) {
      console.error(
        "Error uploading file:",
        error.response ? error.response.data : error
      );
    }
  }
};

const deleteAudioFile = async (index) => {
  isLoadingAudio.value = true;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const fileToDelete = audioFiles.value[index];
  if (!fileToDelete || !fileToDelete.audioFileId) {
    console.error("File data is missing.");
    return;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    console.log("Deleting file...");
    await axios.delete(
      `http://127.0.0.1:5000/deleteAudio/${userId}/${fileToDelete.audioFileId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    console.log("File deleted successfully");
    audioFiles.value.splice(index, 1);

    isLoadingAudio.value = false;
    await fetchAudioFiles();
  } catch (error) {
    console.error(
      "Error deleting the file:",
      error.response ? error.response.data : error
    );
  }
};
</script>

<script>
export default {
  data() {
    return {
      drawerVisible: false,
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
        <input type="text" id="project_name"v-bind:title="title" v-model = "title"/>
      </div>
      <div class="right">
       <!--  <HamburgerMenu /> -->
      </div>
      <div class="centre">
        <div id="playbackControls">
          <p v-if="isLoadingAudio" style="text-align: center">Loading...</p>
          <button v-else id="play_pause" @click="togglePlay">
            <img src="../assets/Play.svg" v-if="!isPlaying" />
            <img src="../assets/Pause.svg" v-else />
          </button>
          <Slider
            :value="volume"
            @update:modelValue="updateVolume"
            :min="0"
            :max="100"
          />

          <audio id="projectAudio" controls style="display: none"></audio>
        </div>
      </div>
      <div class="right">
        <HamburgerMenu />
      </div>
    </div>
    <div class="upload-area" style="text-align: center">
      <div class="first" style="margin-top: 20px">
        <div class="second">
          <table>
            <tr v-for="(audio, index) in audioFiles" :key="index">
              <td class="trackControls">
                <button
                  class="delete"
                  title="Delete Track"
                  @click="deleteAudioFile(index)"
                >
                  <h2>x</h2>
                </button>
                <div class="properties">
                  <textarea placeholder="Enter track name..." v-model="audio.audioFilename"></textarea>
                  <div class="volume">
                    <Slider :value="trackVolumes.value[index]" @update:modelValue="newVolume => debouncedUpdateTrackVolume(index, newVolume)" :min="0" :max="100" />
                    <button title="Solo Track" :style="{
                      backgroundColor: audio.Solo ? 'var(--colour-interactable)' : 'var(--colour-background)',
                      color: audio.Solo ? 'var(--colour-background)' : 'var(--colour-interactable)' 
                    }" @click="toggleTrackSolo(audio)">S</button>
                    <button title="Mute Track" :style="{
                      backgroundColor: audio.Mute ? 'var(--colour-interactable)' : 'var(--colour-background)',
                      color: audio.Mute ? 'var(--colour-background)' : 'var(--colour-interactable)' 
                    }" @click="toggleTrackMute(audio, index)">
                      M
                    </button>
                    <input
                      type="file"
                      :id="'file-input-' + index"
                      @change="(event) => updateFile(index, event)"
                      accept="audio/*"
                      style="display: none"
                    /><button
                      v-if="isLoadingAudio"
                      title="Change Track"
                      style="cursor: not-allowed"
                    >
                      C
                    </button>
                    <button
                      v-else
                      title="Change Track"
                      @click="triggerFileInput(index)"
                    >
                      C
                    </button>
                  </div>
                </div>
                <!-- FOR FUTURE RELEASES. -->
                <!-- <button class="record" title="Record">
                  <h2>•</h2>
                </button> -->
              </td>
              <td class="trackPreview">
                <!-- ALL BELOW VALUES IN SECONDS -->
                <AudioEditor
                  :initOffset = "0.0"
                  :initTrackLength = "180.0"
                  :initFileLength = "10.0"
                />
              </td>
            </tr>
          </table>
        </div>
      </div>
      <input
        type="file"
        id="new-file-input"
        @change="(event) => updateFile(audioFiles.length, event)"
        accept="audio/*"
        style="display: none"
      />
      <p v-if="isLoadingAudio" style="text-align: center; margin-top: 20px">
        Please wait for files to load...
      </p>
      <button
        v-if="isLoadingAudio"
        style="margin-top: 20px; cursor: not-allowed"
        disabled
      >
        Add Audio File
      </button>
      <button v-else @click="triggerNewFileInput" style="margin-top: 20px">
        Add Audio File
      </button>
    </div>
  </div>
</template>

<style scoped>
.upload-area {
  contain: size;
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
  white-space: nowrap;
}

div.second {
  overflow-x: auto;
  margin-left: calc(25% + 0.5em);
  overflow-y: auto;
  height: auto;
}
div.first {
  width: auto;
  overflow-y: auto;
  overflow-x: hidden;
  left: 0;
  top: auto;
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
  overflow:visible;
}

tr .trackPreview .editor {
  height: 6em;
}

.trackControls button.button-muted {
  color: white;
  background-color: #262673;
}

.trackControls button.button-unmuted {
  color: var(--colour-background);
  background-color: var(--colour-interactable);
}

.trackControls button.toggle-button {
  color: var(--colour-background);
  background-color: var(--colour-interactable);
}

.button-muted {
  color: white;
  background-color: #262673;
}

.button-unmuted {
  color: var(--colour-background);
  background-color: var(--colour-interactable);
}

.toggle-button {
  color: white;
  background-color: white;
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
  margin: 0.15em 0 0.4em 0.5em;
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
  width: 15vw;
  margin: 0 auto 0 auto;
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
  padding: 0 0.5em 0 0.5em;
}

#drawer button.close:hover {
  background: none;
}
#drawer button.close:active {
  background: none;
}

.v-btn {
  margin: 0.4em 0.5em 0 0.5em;
}

#track_list .track {
  margin: 1em 0 0 1em;
  padding: 1em 1em 1em 2em;
  background-color: var(--colour-interactable);
  border-radius: 5em 0 0 5em;
}
</style>
