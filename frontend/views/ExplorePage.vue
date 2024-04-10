<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { genres, instruments } from "../assets/globalVariables.js";
import MultipleDropdown from "../components/MultipleDropdown.vue";
import HamburgerMenu from "../components/HamburgerMenu.vue";

const audioSrc = ref("");
const audio = new Audio();
const isPlaying = ref(false);
const currentProject = ref(null);
const currentProjectUser = ref(null);
const searchQuery = ref("");
const errorFile = ref(null);

audio.addEventListener("ended", () => {
  currentProject.value = null;
  isPlaying.value = false;
});

export default {
  name: "ExplorePage",

  setup() {
    const router = useRouter(); // Moved inside setup()
    const projects = ref([]);
    const sortedProjects = ref([]);
    const currentSort = ref("default");
    const searchQuery = ref("");
    const currentFilter = ref("none");
    const selectedInstruments = ref([]);
    const selectedGenres = ref([]);
    const selectedFilters = ref([]);

    const contributeToProject = async (projectId) => {
      const accessToken = localStorage.getItem("userToken");
      const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
      // let projectDetailsString = localStorage.getItem("projectDetails");
      // let projectDetails = JSON.parse(projectDetailsString);
      console.log("contribute function\n" + JSON.stringify(projectId));
      projectId = projectId._id;
      console.log(projectId);

      try {
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

        alert("Project copied successfully!");
        console.log("about to parse");
        console.log(JSON.stringify(response.data.newProject, null, 2)); // Ensure accessing data correctly
        const newProject = JSON.parse(response.data.newProject); // Only needed if newProject is a string
        console.log("about to print");
        console.log("New Project:", newProject);
        console.log("about to redirect");
        clickProject(newProject); // Ensure clickProject can handle the newProject format
      } catch (error) {
        console.error("Error contributing to project:", error);
        alert(error.response?.data.message || "An error occurred");
      }
    };
    const playCombinedAudio = async (projectId, project) => {
      console.log(projectId);
      let combinedAudioId = project.combinedAudioId;
      if (currentProject.value === projectId) {
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
          const response = await axios.get(
            `http://127.0.0.1:5000/streamAudio/${projectId}`,
            {
              responseType: "blob",
            }
          );
          audioSrc.value = URL.createObjectURL(response.data);
          audio.src = audioSrc.value;
          audio.play();
          isPlaying.value = true;
          currentProject.value = projectId;
          errorFile.value = null;
        } catch (error) {
          errorFile.value = projectId;
          console.error("Error fetching audio file:", error);
          alert("There is no preview available for this project");
        }
      }
    };
    const isProjectPlaying = (projectId) => {
      return currentProject.value === projectId && isPlaying.value;
    };

    const fetchAllProjects = async () => {
      const accessToken = localStorage.getItem("userToken");
      const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/getAllProjects`
        );
        projects.value = response.data;
        // add in the upvote/downvote counts
        projects.value.forEach((project) => {
          let likes = 0;
          let dislikes = 0;
          let user_liked = "none";
          if (project.hasOwnProperty("projectUpvote")) {
            project.projectUpvote.forEach((upvote) => {
              if (upvote.like) {
                likes += 1;
              } else {
                dislikes += 1;
              }
              if (upvote.user === userId) {
                user_liked = upvote.like ? "true" : "false";
              }
            });
          }
          project.upvote_count = likes;
          project.downvote_count = dislikes;
          project.user_liked = user_liked;
        });
        sortedProjects.value = [...projects.value];
        console.log(JSON.stringify(projects.value, null, 2));
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    };

    const vote = async (username, project_id, like) => {
      const accessToken = localStorage.getItem("userToken");
      const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
      if (accessToken) {
        try {
          // console.log(username, title);
          await axios.post(
            `http://127.0.0.1:5000/upvoteProject/${userId}/${username}/${project_id}/${like}`,
            {},
            {
              headers: { Authorization: `Bearer ${accessToken}` },
            }
          );
          let updated = false;
          projects.value.forEach((project) => {
            if (
              !updated &&
              project.user === username &&
              project.id === project_id
            ) {
              if (like === "True") {
                if (project.user_liked !== "true") {
                  if (project.user_liked === "false") {
                    project.downvote_count -= 1;
                  }
                  project.upvote_count += 1;
                  project.user_liked = "true";
                } else {
                  project.upvote_count -= 1;
                  project.user_liked = "none";
                }
              } else {
                if (project.user_liked !== "false") {
                  if (project.user_liked === "true") {
                    project.upvote_count -= 1;
                  }
                  project.downvote_count += 1;
                  project.user_liked = "false";
                } else {
                  project.downvote_count -= 1;
                  project.user_liked = "none";
                }
              }
              updated = true;
            }
          });
          setSort(currentSort.value);
        } catch (error) {
          console.error("Error voting on project:", error);
        }
      }
    };

    const setSort = async (sortBy) => {
      currentSort.value = sortBy;
    };

    onMounted(() => {
      fetchAllProjects();
    });

    const filteredProjects = computed(() => {
      // start with reseting the order if in default
      if (currentSort.value === "default") {
        sortedProjects.value = [...projects.value];
      }

      // first do the filtering
      if (selectedFilters.value.length === 0) {
        sortedProjects.value = sortedProjects.value = [...projects.value];
      } else {
        if (selectedFilters.value.includes("hasDescription")) {
          sortedProjects.value = sortedProjects.value.filter(
            (a) => a.description !== ""
          );
        }
        if (selectedFilters.value.includes("hasTitle")) {
          sortedProjects.value = sortedProjects.value.filter(
            (a) => a.title !== ""
          );
        }
        if (selectedFilters.value.includes("hasGenres")) {
          sortedProjects.value = sortedProjects.value.filter(
            (a) => a.genres && a.genres.length > 0
          );
        }
        if (selectedFilters.value.includes("hasInstruments")) {
          sortedProjects.value = sortedProjects.value.filter(
            (a) => a.instruments && a.instruments.length > 0
          );
        }
      }

      sortedProjects.value = sortedProjects.value.filter((project) =>
        project.title.toLowerCase().includes(searchQuery.value.toLowerCase())
      );

      // next filter by the specific genre
      if (selectedGenres.value.length > 0) {
        sortedProjects.value = sortedProjects.value.filter((project) =>
          project.genres?.some((genre) => selectedGenres.value.includes(genre))
        );
      }

      // next filter by the specific instrument
      if (selectedInstruments.value.length > 0) {
        sortedProjects.value = sortedProjects.value.filter((project) =>
          project.instruments?.some((instrument) =>
            selectedInstruments.value.includes(instrument)
          )
        );
      }

      // then do the sorting
      if (currentSort.value === "mostLiked") {
        sortedProjects.value.sort((a, b) => b.upvote_count - a.upvote_count);
      } else if (currentSort.value === "leastLiked") {
        sortedProjects.value.sort((a, b) => a.upvote_count - b.upvote_count);
      } else if (currentSort.value === "mostPopular") {
        sortedProjects.value.sort(
          (a, b) =>
            b.upvote_count -
            b.downvote_count -
            a.upvote_count +
            a.downvote_count
        );
      } else if (currentSort.value === "leastPopular") {
        sortedProjects.value.sort(
          (a, b) =>
            a.upvote_count -
            a.downvote_count -
            b.upvote_count +
            b.downvote_count
        );
      } else if (currentSort.value === "title") {
        sortedProjects.value.sort((a, b) => a.title.localeCompare(b.title));
      } else if (currentSort.value === "user") {
        sortedProjects.value.sort((a, b) => a.user.localeCompare(b.user));
      }
      
      return sortedProjects.value;
    });

    const handleSelectedInstrumentsUpdate = async (updatedSelectedOptions) => {
      selectedInstruments.value = updatedSelectedOptions;
    };

    const handleSelectedGenresUpdate = async (updatedSelectedOptions) => {
      selectedGenres.value = updatedSelectedOptions;
    };

    const handleSelectedFiltersUpdate = async (updatedSelectedOptions) => {
      selectedFilters.value = updatedSelectedOptions;
    };

    const clickProject = async (projectDetails) => {
      try {
        console.log("This is what project should be\n" + projectDetails);
        localStorage.setItem("projectDetails", JSON.stringify(projectDetails));
        setTimeout(() => {
          router.push({
            name: "ProjectView",
            params: { title: projectDetails.title },
          });
        }, 1000);

        console.log("Project opened successfully");
      } catch (error) {
        console.error("Error opening project:", error);
      }
    };

    return {
      projects,
      sortedProjects,
      filteredProjects,
      playCombinedAudio,
      isProjectPlaying,
      errorFile,
      isPlaying,
      searchQuery,
      vote,
      setSort,
      currentSort,
      searchQuery,
      filteredProjects,
      currentFilter,
      handleSelectedInstrumentsUpdate,
      handleSelectedGenresUpdate,
      handleSelectedFiltersUpdate,
      genres: genres,
      instruments: instruments,
      filters: [
        { value: "hasTitle", label: "Has Title" },
        { value: "hasDescription", label: "Has Description" },
        { value: "hasGenres", label: "Has Genres" },
        { value: "hasInstruments", label: "Has Instruments" },
      ],
      selectedGenres,
      selectedInstruments,
      selectedFilters,
      searchQuery,
      contributeToProject,
      clickProject,
    };
  },
  components: { MultipleDropdown, HamburgerMenu },
};
</script>

<template>
  <div class="explorePage">
    <HamburgerMenu />
    <h1>Explore</h1>
    <input
      type="text"
      v-model="searchQuery"
      class="search-input"
      placeholder="Search for projects by name..."
    />
    <div class="dropdowns">
      <MultipleDropdown
        :options="filters"
        valueName="Filters"
        @update:selectedOptions="handleSelectedFiltersUpdate"
      />
      <MultipleDropdown
        :options="genres"
        valueName="Genres"
        @update:selectedOptions="handleSelectedGenresUpdate"
      />
      <MultipleDropdown
        :options="instruments"
        valueName="Instruments"
        @update:selectedOptions="handleSelectedInstrumentsUpdate"
      />
      <select @change="setSort($event.target.value)" class="sort">
        <option value="default">...Sort by</option>
        <option value="mostLiked">Sort by most liked</option>
        <option value="leastLiked">Sort by least liked</option>
        <option value="mostPopular">Sort by most popular</option>
        <option value="leastPopular">Sort by least popular</option>
        <option value="title">Sort by title</option>
        <option value="user">Sort by user</option>
      </select>
    </div>
    <ul>
      <div
        class="track"
        v-for="project in filteredProjects"
        :key="project._id"
        :style="{ position: 'relative' }"
      >
        <div class="leftPanel">
          <h3
            class="title"
            @click="clickProject(project)"
            style="cursor: pointer"
          >
            {{ project.title }}
          </h3>
          <div class="attributes">
            <div class="info">
              <h3 class="creator">{{ project.user }}</h3>
              <div class="description">
                <h3>{{ project.description }}</h3>
                <div>
                  <!-- Container for genres -->
                  <div v-if="project.genres && project.genres.length > 0 ||
                            project.instruments && project.instruments.length > 0"
                  >
                    <p
                      v-for="(genre, index) in project.genres"
                      :key="'genre-' + project._id + '-' + index"
                      class="genre"
                    >
                      sdfsadf{{ genre }}
                    </p>
                    <p
                      v-for="(instrument, index) in project.instruments"
                      :key="'instrument-' + project._id + '-' + index"
                      class="genre"
                    >
                      {{ instrument }}
                    </p>
                  </div>
                </div>
              </div>
              <div
                class="audioError"
                :style="{
                  maxHeight:
                    errorFile == project.title && !isPlaying ? '5em' : '0',
                  // transform: errorFile == project.title && !isPlaying ? 'ScaleY(1)' : 'ScaleY(0)'
                  padding:
                    errorFile == project.title && !isPlaying
                      ? '0.2em 0.5em 0.25em 0.5em'
                      : '0',
                  marginTop:
                    errorFile == project.title && !isPlaying ? '0.25em' : '0',
                  color:
                    errorFile == project.title && !isPlaying
                      ? 'var(--colour-background)'
                      : '#00000000',
                }"
              >
                <div v-if="errorFile == project.title && !isPlaying">
                  Error: Unable to fetch project audio
                </div>
              </div>
            </div>
          </div>
          <div>
            <p>{{ project.date.substring(0,16) }}</p>
          </div>
        </div>

        <div class="interact">
          <button
            class="contribute"
            @click="contributeToProject(project)"
            :style="{
              backgroundColor: 'white',
              color: '#77a4f9',
              padding: '5px',
              borderRadius: '5px',
              fontWeight: 'bold',
            }"
          >
            Contribute
          </button>
          <div class="likeDislike">
            <button
              @click="vote(project.user, project.id, 'True')"
              class="like"
            >
              <img src="../assets/Like.svg" /> {{ project.upvote_count }}
            </button>
            <button
              @click="vote(project.user, project.id, 'False')"
              class="dislike"
            >
              <img src="../assets/Dislike.svg" /> {{ project.downvote_count }}
            </button>
          </div>
        </div>
        <button @click="playCombinedAudio(project._id, project)">
          <img
            class="play"
            src="../assets/Play.svg"
            v-if="!isProjectPlaying(project._id)"
          />
          <img
            class="play"
            src="../assets/Pause.svg"
            v-else
          />
        </button>
      </div>
    </ul>
  </div>
</template>

<style scoped>
.explorePage {
  text-align: center;
  min-height: 100vh;
  background-color: var(--colour-panel-soft);
  padding-bottom: 1em;
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
  background-image: url("../assets/search.svg");
  background-repeat: no-repeat;
  background-position: 8px 50%;
  background-size: 20px 20px;
  background-color: var(--colour-background);
  margin-bottom: 1em;
  font-size: medium;
  outline: none;
  color: var(--colour-text);
  transition: box-shadow 200ms;
}
.search-input:focus {
  box-shadow: 0em 0.05em 0.5em 0.01em var(--colour-dropshadow);
}
.search-input::placeholder {
  color: var(--colour-interactable);
}

.dropdowns {
  display: flex;
  justify-content: center;
  width: 50%;
  margin: 0 auto 0 auto;
}

.dropdowns .multiple-dropdown {
}

.dropdowns .sort {
  text-align-last: right;
  direction: rtl;
  margin-left: auto;
  color: var(--colour-text);
  border-radius: 0.5em;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  cursor: pointer;
}

.dropdowns .sort * {
  border: none;
  background-color: var(--colour-background);
}

.dropdowns option:checked,
.dropdowns option:hover {
  background-color: var(--colour-background);
  color: var(--colour-text);
}

.track {
  background-color: var(--colour-background);
  color: var(--colour-background);
  width: 50%;
  text-align: left;
  display: flex;
  align-items: center;
  padding: 0.5em;
  margin: 0 auto 1em auto;
  border-radius: 1em;
  overflow: hidden;
  transition: box-shadow 300ms;
  box-shadow: 0em 0.05em 0.5em 0.01em var(--colour-dropshadow);
}

.track .leftPanel {
  width: 60%;
  align-self: flex-start;
  margin-right: 0.75em;
  overflow: hidden;
  background-color: var(--colour-interactable);
  box-shadow: -11em 0 0 11.75em var(--colour-interactable);
}

.track .title {
  font-family: "Delta Gothic One";
}

.track .attributes {
  display: flex;
}

.track .info {
  flex: 1;
}

.track .info .creator {
  font-style: italic;
  font-weight: 600;
}

.track .description {
  font-size: smaller;
  word-wrap: break-word;
  color: var(--colour-text);
  padding-left: 0.25em;
  margin-top: 0.25em;
  flex: 1;
  align-self: stretch;
  border-radius: 0.5em;
  background-color: var(--colour-background);
}

.audioError {
  color: var(--colour-background);
  background-color: var(--colour-warning);
  width: fit-content;
  line-height: 1em;
  padding: 0.2em 0.5em 0.25em 0.5em;
  border-radius: 0.5em;
  transition: all 250ms;
}

.track .likeDislike button {
  color: var(--colour-background);
  background-color: var(--colour-interactable);
  padding: 0.3em 0 0.3em 0;
  border-radius: 0.25em;
  width: 3em;
}

.track .likeDislike button.like {
  margin-right: 0.5em;
}

.track .likeDislike button img {
  height: 1em;
  color: var(--colour-background);
}

.track .likeDislike button.dislike img {
  position: relative;
  top: 0.2em;
}

.track .audioPreview {
  flex: 1;
}

.track .play {
  margin: 0 0.5em 0 0;
  filter: invert(40%) sepia(42%) saturate(559%) hue-rotate(182deg) brightness(100%) contrast(96%);
}

.track .interact {
  text-align: center;
  margin: 0 auto 0 auto;
}

.track .interact button.contribute {
  width: 100%;
  margin-bottom: 0.5em;
  color: var(--colour-background) !important;
  background-color: var(--colour-interactable) !important;
}

.genre {
  display: inline-block;
  margin: 0.25em 0.25em 0.25em 0;
  font-weight: 600;
  color: var(--colour-background);
  background-color: var(--colour-interactable);
  padding: 0 0.25em 0 0.25em;
  border-radius: 0.5em;
}

.search-input {
  width: 50%;
  padding: 0.5em 2em 0.5em 2em;
  border: 0px solid var(--colour-interactable);
  border-radius: 0.5em;
  flex: 0.5;
  margin-top: 1em;
  background-image: url("../assets/search.svg"); /* Path to your search icon */
  background-repeat: no-repeat;
  background-position: 8px 50%;
  background-size: 20px 20px;
  background-color: var(--colour-background);
  margin-bottom: 1em;
  font-size: medium;
  outline: none;
  color: var(--colour-text);
}
.search-input::placeholder {
  color: var(--colour-interactable);
}

@media (max-width: 900px) {
  .track {
    width: 90%;
    margin: 0 auto 1em auto;
  }
  .dropdowns {
    width: 90%;
  }
}
</style>
