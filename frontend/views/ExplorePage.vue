<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import HamburgerMenu from "../components/HamburgerMenu.vue";

const audioSrc = ref("");
const audio = new Audio();
const isPlaying = ref(false);
const currentProject = ref(null);
const searchQuery = ref("");
const errorFile = ref(null);

audio.addEventListener("ended", () => {
  currentProject.value = null;
  isPlaying.value = false;
});

export default {
  name: "ExplorePage",

  setup() {
    const projects = ref([]);
    const playCombinedAudio = async (username, title) => {
      if (currentProject.value === title) {
        if (isPlaying.value) {
          audio.pause();
        } else {
          audio.play();
        }
        isPlaying.value = !isPlaying.value;
      } else {
        audio.pause();
        isPlaying.value = false;
        currentProject.value = null;

        try {
          //console.log(username, title);
          const response = await axios.get(
            `http://127.0.0.1:5000/explorePageAudio/${username}/${title}`,
            {
              responseType: "blob",
            }
          );
          audioSrc.value = URL.createObjectURL(response.data);
          audio.src = audioSrc.value;
          audio.play();
          isPlaying.value = true;
          currentProject.value = title;
          errorFile.value=null;
        } catch (error) {
          errorFile.value = title;
          console.error("Error fetching audio file:", error);
        }
      }
    };
    const isProjectPlaying = (project) => {
      return currentProject.value === project && isPlaying.value;
    };

    const fetchAllProjects = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/getAllProjects`
        );
        projects.value = response.data;
        console.log(JSON.stringify(projects.value));
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    };
    onMounted(() => {
      fetchAllProjects();
    });
    const filteredProjects = computed(() => {
      let filtered = [];
      filtered = projects.value.filter(project => project.title.toLowerCase().includes(searchQuery.value.toLowerCase()));
      return filtered;
    });

    return {
      projects,
      filteredProjects,
      playCombinedAudio,
      isProjectPlaying,
      errorFile,
      isPlaying,
      searchQuery
    };
  },
  components: {HamburgerMenu}
};
</script>

<template>
  <div class="explorePage">
    <h1>Explore</h1>

    <HamburgerMenu />

      <input type="text" v-model="searchQuery" class="search-input" placeholder="Search for projects by name...">
    <ul>
      
      <div class="track" v-for="project in filteredProjects">
        <div class="info">
          <h3 class="title">{{ project.title }}</h3>
          <h3 class="creator">{{ project.user }}</h3>
        </div>
        <h3 class="description">{{ project.description }}</h3>
        <div class="likeDislike">
          <button class="like">like {{ 0 }}</button>
          <button>dislike {{ 0 }}</button>
        </div>
        <div  v-if="errorFile==project.title && !isPlaying" class="audioError">Error: Unable to fetch project audio</div>
        <div class="audioPreview"></div>
        <button
          class="play"
          @click="playCombinedAudio(project.user, project.title)"
        >
          <img
            src="../assets/Play.svg"
            v-if="!isProjectPlaying(project.title)"
          />
          <img src="../assets/Pause.svg" v-else />
        </button>
      </div>
    </ul>
  </div>
  
</template>

<style scoped>
.explorePage {
  height: 100vh;
  text-align: center;
  background-color: var(--colour-panel-soft);
}

h1 {
  font-family: "Delta Gothic One";
  padding: 0.5em;
}

.search-input {
  width: 50%;
  padding: 0.5em 2em 0.5em 2em;
  border: 0px solid var(--colour-interactable);
  border-radius: 0.5em;
  flex: 0.5;
  margin-top: 1em;
  background-image: url('../assets/search.svg'); /* Path to your search icon */
  background-repeat: no-repeat;
  background-position: 8px 50%;
  background-size: 20px 20px;
  background-color: var(--colour-background);
  margin-bottom: 1em; 
  font-size: medium;
  outline: none;
  color: var(--colour-text)
}
.search-input::placeholder {
  color: var(--colour-interactable);
}
.audioError{
  position: relative; 
  transform: translate(75%, 30%);
  color: maroon;
}

.track {
  background-color: var(--colour-interactable);
  color: var(--colour-background);
  text-align: left;
  display: flex;
  padding: 0.5em;
  margin: 0 1em 1em 1em;
  border-radius: 1em;
}

.track .info .title {
  font-family: "Delta Gothic One";
}
.track .info .creator {
  font-style: italic;
}

.track .description {
  font-size: medium;
  word-wrap: break-word;
  color: var(--colour-text);
  padding: 0 0.5em 0 0.5em;
  margin-left: 0.5em;
  flex: 0.5;
  border-radius: 0.5em;
  background-color: var(--colour-background);
}

.track .likeDislike {
  display: flex;
  flex-direction: column;
}

.track .likeDislike button {
  color: var(--colour-interactable);
  background-color: var(--colour-background);
  padding: 0 0.25em 0 0.25em;
  margin-left: 0.5em;
  border-radius: 0.25em;
}

.track .likeDislike button.like {
  margin-bottom: 0.5em;
}

.track .likeDislike button {
  color: var(--colour-interactable);
  background-color: var(--colour-background);
  font-weight: 600;
  padding: 0 0.25em 0 0.25em;
  border-radius: 0.25em;
}

.track .audioPreview {
  flex: 1;
}

.track .play {
  margin-right: 0.5em;
}
</style>
