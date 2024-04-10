<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import Slider from "../components/Slider.vue";
import HamburgerMenu from "../components/HamburgerMenu.vue";
import AudioEditor from "../components/AudioEditor.vue";
import { genres, instruments } from "../assets/globalVariables.js";
import MultipleDropdown from "../components/MultipleDropdown.vue";
import axios from "axios";

const router = useRouter();
const route = useRoute();
const title = ref(router.currentRoute.value.params.title);
let oldTitle = title.value;
const audioFiles = ref([]);
const volume = ref(100);
const isPlaying = ref(false);
const audioSrc = ref("");
const comment = ref("");
const comments = ref([]);
const combinedAudioReady = ref(false);
const isLoadingAudio = ref(true);
const trackVolumes = [20, 40, 60, 100];
const trackStartPositions = [0, 0, 0, 0];
const newCommentText = ref("");
const areCommentsOpen = ref(false);
let isOwnProfile = ref(true);
const upvotes = ref(0);
const downvotes = ref(0);

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

const getVotes = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  let projectDetailsString = localStorage.getItem("projectDetails");
  let projectDetails = JSON.parse(projectDetailsString);
  const response = await axios.get(
    `http://127.0.0.1:5000/getVotes/${projectDetails._id}`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  let data = response.data;
  upvotes.value = data.upvotes;
  downvotes.value = data.downvotes;
};

const vote = async (like) => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  let projectDetailsString = localStorage.getItem("projectDetails");
  let projectDetails = JSON.parse(projectDetailsString);
  let projectId = projectDetails._id;
  if (accessToken) {
    try {
      // console.log(username, title);
      await axios.post(
        `http://127.0.0.1:5000/upvoteProject/${userId}/${projectId}/${like}`,
        {},
        {
          headers: { Authorization: `Bearer ${accessToken}` },
        }
      );
    } catch (error) {
      console.error("Error voting on project:", error);
    }
  }
  getVotes();
};

const fetchComments = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  let projectDetailsString = localStorage.getItem("projectDetails");
  let projectDetails = JSON.parse(projectDetailsString);

  const response = await axios.get(
    `http://127.0.0.1:5000/getComments/${projectDetails._id}`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  comments.value = response.data;

  comments.value.sort((a, b) => {
    const dateA = new Date(a.date);
    const dateB = new Date(b.date);
    return dateA < dateB ? 1 : dateA > dateB ? -1 : 0;
  });

  const now = new Date();

  comments.value.forEach((c) => {
    // check if its the right user
    c["canDelete"] = userId == c["user"];

    let seconds = Math.floor((now - new Date(c.date)) / 1000);

    if (seconds < 60) {
      c.date = `${seconds} second${seconds === 1 ? "" : "s"} ago`;
    } else if (seconds < 3600) {
      seconds = Math.floor(seconds / 60);
      c.date = `${seconds} minute${seconds === 1 ? "" : "s"} ago`;
    } else if (seconds < 86400) {
      seconds = Math.floor(seconds / 3600);
      c.date = `${seconds} hour${seconds === 1 ? "" : "s"} ago`;
    } else if (seconds < 31536000) {
      seconds = Math.floor(seconds / 86400);
      c.date = `${seconds} day${seconds === 1 ? "" : "s"} ago`;
    } else {
      seconds = Math.floor(seconds / 31536000);
      c.date = `${seconds} year${seconds === 1 ? "" : "s"} ago`;
    }
    console.log(c.date);
  });
};

const submitComment = async (c) => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  let projectDetailsString = localStorage.getItem("projectDetails");
  let projectDetails = JSON.parse(projectDetailsString);
  let projectId = projectDetails._id;
  try {
    let max =
      comments.value.length > 0
        ? comments.value.reduce(
            (max, c) => (parseInt(c.id) > max ? parseInt(c.id) : max),
            parseInt(comments.value[0].id)
          )
        : 0;
    const commentData = {
      comment: comment.value,
      date: new Date(),
      id: max + 1,
    };
    const response = await axios.post(
      `http://127.0.0.1:5000/addComment/${userId}/${projectId}`,
      commentData,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    comment.value = "";
    fetchComments();
  } catch (error) {
    console.error("Error fetching comments", error);
  }
};

const deleteComment = async (id) => {
  const accessToken = localStorage.getItem("userToken");
  let projectDetailsString = localStorage.getItem("projectDetails");
  let projectDetails = JSON.parse(projectDetailsString);
  let projectId = projectDetails._id;
  await axios.delete(`http://127.0.0.1:5000/deleteComment/${projectId}/${id}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  comments.value = comments.value.filter((c) => c.id !== id);
};

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
function normalizeProjectDetails(projectDetails) {
  let normalizedDetails = { ...projectDetails };

  // Convert _id if it's in object format
  if (typeof normalizedDetails._id === "object" && normalizedDetails._id.$oid) {
    normalizedDetails._id = normalizedDetails._id.$oid;
  }

  // Check and convert combinedAudioId if necessary
  if (
    normalizedDetails.combinedAudioId &&
    typeof normalizedDetails.combinedAudioId === "object" &&
    normalizedDetails.combinedAudioId.$oid
  ) {
    normalizedDetails.combinedAudioId = normalizedDetails.combinedAudioId.$oid;
  }

  // If there are other fields with similar structure, convert them here

  return normalizedDetails;
}

async function streamAllAudioFiles() {
  isLoadingAudio.value = true;

  let projectDetailsString = localStorage.getItem("projectDetails");
  let projectDetails = JSON.parse(projectDetailsString);
  let normalizedProjectDetails = normalizeProjectDetails(projectDetails);
  if (!projectDetailsString) {
    console.error("Project details not found.");
    isLoadingAudio.value = false;
    return;
  }

  const projectId = normalizedProjectDetails._id;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const accessToken = localStorage.getItem("userToken");

  try {
    // First, ensure the audio files are combined in the backend and get the ID for the combined audio.
    let combineResponse = await axios.get(
      `http://127.0.0.1:5000/streamProjectAudios/${projectId}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );

    console.log(
      "Audio files combined successfully:",
      combineResponse.data.combinedAudioId
    );

    // Step 2: Stream the Combined Audio
    const combinedAudioId = combineResponse.data.combinedAudioId;
    const combinedAudioUrl = `http://127.0.0.1:5000/streamAudio/${combinedAudioId}`;
    audioSrc.value = combinedAudioUrl;

    console.log("Preparing to stream combined audio files...");
    await new Promise((resolve, reject) => {
      const audioPlayer = document.getElementById("projectAudio");
      audioPlayer.src = audioSrc.value;

      audioPlayer.onloadeddata = () => {
        console.log("Audio data has loaded and is now ready to play");
        isLoadingAudio.value = false;
        resolve();
      };

      audioPlayer.onerror = (event) => {
        console.error("Error loading combined audio", event);
        isLoadingAudio.value = false;
        reject(new Error("Error loading combined audio"));
      };
      audioPlayer.load();
    });

    combinedAudioReady.value = true;
  } catch (error) {
    console.error("Error in combining or streaming audio files:", error);
    isLoadingAudio.value = false;
  }
}

async function fetchAudioFiles() {
  isLoadingAudio.value = true;
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
  let projectDetailsString = localStorage.getItem("projectDetails");
  console.log(projectDetailsString);
  let projectDetails = JSON.parse(projectDetailsString);
  console.log(projectDetails);

  // Conditionally set projectId based on the _id type
  let projectId;
  if (typeof projectDetails._id === "object" && projectDetails._id.$oid) {
    projectId = projectDetails._id.$oid; // If _id is an object with $oid
  } else {
    projectId = projectDetails._id; // If _id is a string
  }

  try {
    const response = await axios.get(
      `http://127.0.0.1:5000/getProjectDetails/${projectId}/${userId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    console.log("Audio files and project ownership fetched:", response.data);
    audioFiles.value =
      response.data.audioFiles?.map((file) => ({
        ...file,
        src: `http://127.0.0.1:5000/streamAudio/${file.audioFileId}`,
      })) || [];

    trackVolumes.value = audioFiles.value.map((file) => file.Volumes);
    trackStartPositions.value = audioFiles.value.map(
      (file) => file.Start_Position
    );

    isOwnProfile = response.data.isOwnProfile;
    console.log("Is this the user's own project?:", isOwnProfile);
  } catch (error) {
    console.error("Error fetching project details:", error);
  } finally {
    isLoadingAudio.value = false;
  }
}

onMounted(async () => {
  await fetchAudioFiles();
  await fetchComments();
  await getVotes();
});

onMounted(() => {
  getVotes();
});

function updateVolume(newVolume) {
  const volumeValue = newVolume / 100;
  const audioPlayer = document.getElementById("projectAudio");
  audioPlayer.volume = volumeValue;
}

/* qweoifnqwpeiofubqweifubqweofiubqweofiuqbweofiuqbwefoiuqwbefoqiuwefoqwieufbqwef */
async function updateTrackVolume(audio, index, newVolume) {
  isLoadingAudio.value = true;

  audio.Volumes = newVolume;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  const indexString = String(index);
  const volumeString = String(newVolume);

  try {
    console.log("Combining all audio files in the backend...");
    const volumeResponse = await axios.get(
      `http://127.0.0.1:5000/updateAudioVolume/${userId}/${encodeURIComponent(
        title.value
      )}/${indexString}/${volumeString}`,
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
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => func.apply(context, args), delay);
  };
}

async function updateTrackMute(audio, index) {
  isLoadingAudio.value = true;

  audio.Mute = !audio.Mute;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  console.log("Muted!!!!!");

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  const indexString = String(index);

  try {
    console.log("Muting File in the backend...");
    const muteResponse = await axios.get(
      `http://127.0.0.1:5000/updateTrackMute/${userId}/${encodeURIComponent(
        title.value
      )}/${indexString}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );

    streamAllAudioFiles();
  } catch (error) {
    console.error("Error combining or streaming audio files:", error);
  }
}

async function updateTrackSolo(audio, index) {
  isLoadingAudio.value = true;

  audio.Solo = !audio.Solo;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  console.log("Muted!!!!!");

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  const indexString = String(index);

  try {
    console.log("Muting File in the backend...");
    const soloResponse = await axios.get(
      `http://127.0.0.1:5000/updateTrackSolo/${userId}/${encodeURIComponent(
        title.value
      )}/${indexString}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );

    streamAllAudioFiles();
  } catch (error) {
    console.error("Error combining or streaming audio files:", error);
  }
}

const debouncedUpdateTrackPosition = debounce(updateTrackPosition, 500);
async function updateTrackPosition(audio, index, trackPos) {
  isLoadingAudio.value = true;

  console.log("New Position: ");
  console.log(trackPos);

  audio.Start_Position = trackPos;

  const audioPlayer = document.getElementById("projectAudio");
  if (isPlaying.value) {
    audioPlayer.pause();
    isPlaying.value = false;
  }

  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  const indexString = String(index);
  const trackPosString = String(trackPos);

  try {
    console.log("Combining all audio files in the backend...");
    const positionResponse = await axios.get(
      `http://127.0.0.1:5000/updateAudioPosition/${userId}/${encodeURIComponent(
        title.value
      )}/${indexString}/${trackPosString}`,
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );

    streamAllAudioFiles();
  } catch (error) {
    console.error("Error combining or streaming audio files:", error);
  }
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
    let projectDetailsString = localStorage.getItem("projectDetails");
    console.log(projectDetailsString);
    let projectDetails = JSON.parse(projectDetailsString);
    console.log(projectDetails);

    // Conditionally set projectId based on the _id type
    let projectId;
    if (typeof projectDetails._id === "object" && projectDetails._id.$oid) {
      projectId = projectDetails._id.$oid; // If _id is an object with $oid
    } else {
      projectId = projectDetails._id; // If _id is a string
    }

    try {
      console.log("Uploading file...");
      const response = await axios.post(
        `http://127.0.0.1:5000/uploadAudioToProject/${userId}/${projectId}/${index}`, // Updated URL
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
  let projectDetailsString = localStorage.getItem("projectDetails");
  console.log(projectDetailsString);
  let projectDetails = JSON.parse(projectDetailsString);
  console.log(projectDetails);

  // Conditionally set projectId based on the _id type
  let projectId;
  if (typeof projectDetails._id === "object" && projectDetails._id.$oid) {
    projectId = projectDetails._id.$oid; // If _id is an object with $oid
  } else {
    projectId = projectDetails._id; // If _id is a string
  }

  try {
    console.log("Deleting file...");
    await axios.delete(
      `http://127.0.0.1:5000/deleteAudio/${projectId}/${fileToDelete.audioFileId}`,
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
const sendTrackNameUpdate = async (audioFileId, newFilename) => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
  let projectTitle = title.value;
  console.log(userId);
  console.log(newFilename);
  try {
    console.log("Updating file name...");
    const response = await axios.put(
      `http://127.0.0.1:5000/updateAudioFilename/${userId}/${audioFileId}`,
      { audioFilename: newFilename, projectTitle: projectTitle }, // add projectTitle here
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    console.log("File name updated successfully", response.data);
    // Handle any additional state updates or UI feedback here
  } catch (error) {
    console.error(
      "Error updating the file name:",
      error.response ? error.response.data : error
    );
    // Handle error state or UI feedback here
  }
};
const sendProjectTitleUpdate = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;

  try {
    console.log("Updating project title...");
    const response = await axios.put(
      `http://127.0.0.1:5000/updateProjectTitle/${userId}`,
      { oldProjectTitle: oldTitle, newProjectTitle: title.value },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    console.log("Project title updated successfully", response.data);
    // Update oldTitleValue to the new title after a successful update
    oldTitle = title.value;
  } catch (error) {
    console.error(
      "Error updating the project title:",
      error.response ? error.response.data : error
    );
  }
};

const contributeToProject = async () => {
  const accessToken = localStorage.getItem("userToken");
  const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
  let projectDetailsString = localStorage.getItem("projectDetails");
  console.log(projectDetailsString);
  let projectDetails = JSON.parse(projectDetailsString);
  console.log(projectDetails);

  // Conditionally set projectId based on the _id type
  let projectId;
  if (typeof projectDetails._id === "object" && projectDetails._id.$oid) {
    projectId = projectDetails._id.$oid; // If _id is an object with $oid
  } else {
    projectId = projectDetails._id; // If _id is a string
  }
  try {
    const accessToken = localStorage.getItem("userToken");
    // Make the post request and wait for the response
    const response = await axios.post(
      `http://127.0.0.1:5000/contributeToProject`,
      {
        projectId: projectId,
        userId: userId,
      },
      {
        headers: { Authorization: `Bearer ${accessToken}` },
      }
    );

    // If the response is successful, execute the following
    alert("Project copied successfully!");
    console.log("about to parse");
    const newProject = JSON.parse(response.data.newProject);
    consol.log("about to print");
    console.log("New Project:", newProject);
    console.log("about to redirect");
    clickProject(newProject); // Use the new project's _id to handle the project
  } catch (error) {
    // If there is an error, log it and show an alert
    console.error("Error contributing to project:", error);
    alert(error.response?.data.message || "An error occurred");
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
    <div class="likeDislike">
          <button @click="vote('True')" class="like">
            <img src="../assets/Like.svg" /> {{ upvotes }}
          </button>
          <button @click="vote('False')" class="dislike">
            <img src="../assets/Dislike.svg" /> {{ downvotes }}
          </button>
        </div>
    <button
      class="comments-button"
      @click="
        () => {
          areCommentsOpen = true;
        }
      "
    >
      comments
    </button>
    <div
      class="comments-area"
      :style="{
        maxHeight: areCommentsOpen ? '15em' : '0',
        boxShadow: areCommentsOpen
          ? '0 0 0.5em var(--colour-dropshadow)'
          : 'none',
        zIndex: areCommentsOpen ? '' : '-1',
      }"
    >
      <button
        class="close-comments"
        @click="
          () => {
            areCommentsOpen = false;
          }
        "
        :style="{
          display: areCommentsOpen ? '' : 'none',
        }"
      >
        x
      </button>
      <div
        class="comments-box"
        style="
          margin-top: 10px;
          justify-content: center;
          display: flex;
          align-items: center;
        "
      >
        <textarea
          type="text"
          v-model="comment"
          class="addComment"
          placeholder="Comment..."
        />
        <button @click="submitComment">Post</button>
      </div>
      <div>
        <ul>
          <div class="comments" v-for="com in comments" :key="com._id">
            <div class="box">
              <h3 class="user" style="font-weight: bold">{{ com.username }}</h3>
            </div>
            <div class="box">
              <h3 class="user" style="font-weight: bold">{{ com.date }}</h3>
            </div>
            <div class="box">
              <h3 class="description">{{ com.comment }}</h3>
            </div>
            <button v-if="com.canDelete" @click="deleteComment(com.id)">
              Delete
            </button>
          </div>
        </ul>
      </div>
    </div>
    <div id="ribbon">
      <div class="left">
        <div class="dropdowns"></div>
        <input
          type="text"
          id="project_name"
          :title="title.value"
          v-model="title"
          @keyup.enter.stop="sendProjectTitleUpdate"
        />
      </div>
      <div class="right"></div>
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
      <div class="right"></div>
    </div>
    <div class="upload-area" style="text-align: center">
      <div class="first" style="margin-top: 20px">
        <div class="second">
          <table>
            <tr v-for="(audio, index) in audioFiles" :key="index">
              <td
                class="trackControls"
                :style="{
                  paddingTop: isOwnProfile ? '' : '1em',
                }"
              >
                <template v-if="isOwnProfile">
                  <button
                    class="delete"
                    title="Delete Track"
                    @click="deleteAudioFile(index)"
                  >
                    <h2>x</h2>
                  </button>
                </template>
                <div
                  class="properties"
                  :style="{
                    marginLeft: isOwnProfile ? '' : '2em',
                  }"
                >
                  <template v-if="isOwnProfile">
                    <textarea
                      placeholder="Enter track name..."
                      v-model="audio.audioFilename"
                      @keyup.enter.stop="
                        sendTrackNameUpdate(
                          audio.audioFileId,
                          audio.audioFilename
                        )
                      "
                    ></textarea>
                  </template>
                  <template v-else>
                    <textarea
                      placeholder="Enter track name..."
                      v-model="audio.audioFilename"
                      @keyup.enter.stop="
                        sendTrackNameUpdate(
                          audio.audioFileId,
                          audio.audioFilename
                        )
                      "
                      disabled
                    ></textarea>
                  </template>

                  <template v-if="isOwnProfile">
                    <div class="volume">
                      <Slider
                        :value="audio.Volumes"
                        @update:modelValue="
                          (newVolume) =>
                            debouncedUpdateTrackVolume(audio, index, newVolume)
                        "
                        :min="0"
                        :max="100"
                        :style="{
                          pointerEvents: isLoadingAudio ? 'none' : 'auto',
                        }"
                      />
                      <button
                        title="Solo Track"
                        :style="{
                          backgroundColor: audio.Solo
                            ? 'var(--colour-interactable)'
                            : 'var(--colour-background)',
                          color: audio.Solo
                            ? 'var(--colour-background)'
                            : 'var(--colour-interactable)',
                          pointerEvents: isLoadingAudio ? 'none' : 'auto',
                        }"
                        @click="updateTrackSolo(audio, index)"
                      >
                        S
                      </button>
                      <button
                        title="Mute Track"
                        :style="{
                          backgroundColor: audio.Mute
                            ? 'var(--colour-interactable)'
                            : 'var(--colour-background)',
                          color: audio.Mute
                            ? 'var(--colour-background)'
                            : 'var(--colour-interactable)',
                          pointerEvents: isLoadingAudio ? 'none' : 'auto',
                        }"
                        @click="updateTrackMute(audio, index)"
                      >
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
                        style="display: none"
                      >
                        C
                      </button>
                      <button
                        v-else
                        title="Change Track"
                        @click="() => triggerFileInput(index)"
                        style="display: none"
                      >
                        C
                      </button>
                    </div>
                  </template>
                </div>
              </td>
              <td class="trackPreview">
                <template v-if="isOwnProfile">
                  <AudioEditor
                    @update:offset="
                      (trackPos) =>
                        debouncedUpdateTrackPosition(audio, index, trackPos)
                    "
                    :initOffset="audio.Start_Position"
                    :initTrackLength="180.0"
                    :initFileLength="10.0"
                    :style="{ pointerEvents: isLoadingAudio ? 'none' : 'auto' }"
                  />
                </template>

                <template v-else>
                  <AudioEditor
                    @update:offset="
                      (trackPos) =>
                        debouncedUpdateTrackPosition(audio, index, trackPos)
                    "
                    :initOffset="audio.Start_Position"
                    :initTrackLength="180.0"
                    :initFileLength="10.0"
                    style="pointer-events: none"
                /></template>
              </td>
            </tr>
          </table>
        </div>
      </div>
      <template v-if="isOwnProfile">
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
          style="margin: 20px; cursor: not-allowed"
          disabled
        >
          Add New Track
        </button>
        <button v-else @click="triggerNewFileInput" style="margin-top: 20px">
          Add New Track
        </button> </template
      ><template v-else
        ><p v-if="isLoadingAudio" style="text-align: center; margin: 20px">
          Please wait for files to load...
        </p>
        <button
          v-if="isLoadingAudio"
          style="margin-top: 20px; cursor: not-allowed"
          disabled
        >
          Contribute
        </button>
        <button v-else @click="contributeToProject" style="margin-top: 20px">
          Contribute
        </button></template
      >
    </div>
    <HamburgerMenu />
  </div>
</template>

<style scoped>
#app {
  overflow: hidden !important;
}
.projectPage {
  /* min-height: 100vh; */
}
.upload-area {
  margin-top: 6em;
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
  width: 0px;
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

.comments {
  background-color: var(--colour-panel-soft);
  color: var(--colour-text);
  text-align: left;
  display: flex;
  padding: 0.5em;
  margin: 0 1em 1em 1em;
  border-radius: 1em;
  flex-direction: column; /* Change flex-direction to column */
  max-height: 200px; /* Set a maximum height for the comments box */
  overflow-y: auto;
}

.comments .box {
  font-family: "Fredoka";
  font-size: 12px;
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
  overflow: visible;
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
  position: fixed;
  top: 0;
  contain: layout;
  background-color: var(--colour-panel-soft);
  box-shadow: 0 0 0.5em var(--colour-dropshadow);
  padding: 0.5em 0 0 0;
  z-index: 5;
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
  margin: 0.55em 0 0 0.5em;
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

.comments-area {
  position: fixed;
  overflow-y: scroll;
  width: 100%;
  bottom: 0;
  padding-bottom: 1em;
  background-color: var(--colour-background);
  border-radius: 1em;
  transition: all 100ms;
}

.comments-button {
  position: fixed;
  bottom: 0;
  right: 0;
  margin: 1em;
}

.comments-area button.close-comments {
  font-family: "Fredoka";
  position: fixed;
  left: 0;
  border-radius: 0 0 1em 0;
}

.addComment {
  width: 50%;
  height: 4em;
  resize: none;
  padding: 0.5em 2em 0.5em 2em;
  border: 0px solid var(--colour-interactable);
  border-radius: 0.5em;
  flex: 0.5;
  margin-top: 1em;
  background-image: url("../assets/comment.png");
  background-repeat: no-repeat;
  background-position: 5px 20%;
  background-size: 20px 20px;
  background-color: var(--colour-panel-soft);
  margin-bottom: 1em;
  font-size: medium;
  outline: none;
  resize: vertical;
  overflow-y: auto;
  color: var(--colour-text);
}
.addComment::placeholder {
  color: var(--colour-interactable);
}
.comments-box button {
  margin: 1em 0 0 0.5em;
  height: calc(4em);
  align-self: flex-start;
}

.comments {
  background-color: var(--colour-panel-soft);
  color: var(--colour-text);
  text-align: left;
  display: flex;
  padding: 0.5em;
  margin: 0 1em 1em 1em;
  border-radius: 1em;
  flex-direction: column; /* Change flex-direction to column */
  max-height: 200px; /* Set a maximum height for the comments box */
  overflow-y: auto;
  z-index: -5001;
}

.comments .box {
  font-family: "Fredoka";
  font-size: 12px;
}
.separatorLine {
  position: relative;
  width: 90%;
  left: 5%;
  height: 0.5em;
  background-color: #77afff;
  border-radius: 10px;
  margin-top: 3vh;
  z-index: -5001;
}

.track .likeDislike button {
  color: var(--colour-background);
  background-color: var(--colour-interactable);
  padding: 0.3em 0 0.3em 0;
  border-radius: 0.25em;
  width: 3em;
}

.likeDislike {
  position: fixed;
  bottom: 0;
  margin: 1em;
}
.likeDislike button.like {
  margin-right: 0.5em;
}

.likeDislike button img {
  height: 1em;
  color: var(--colour-background);
}

.likeDislike button.dislike img {
  position: relative;
  top: 0.2em;
}
</style>
