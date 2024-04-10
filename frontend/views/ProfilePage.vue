<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import blankProfilePicture from "../assets/blankProfilePicture.png";
import { useRouter } from "vue-router";
import { genres, instruments } from '../assets/globalVariables.js';
import MultipleDropdown from "../components/MultipleDropdown.vue";
import HamburgerMenu from "../components/HamburgerMenu.vue";

export default {
    name: "ProfilePage",
    setup() {
        const username = ref("Loading...");
        const showAddProjectPopup = ref(false);
        const newProjectTitle = ref("");
        const newProjectDescription = ref("");
        const projects = ref([]);
        const profilePictureUrl = ref(blankProfilePicture);
        const fileInput = ref(null);
        const router = useRouter();
        const onClickFileInput = () => fileInput.value.click();
        const selectedInstruments = ref([]);
        const selectedGenres = ref([]);
        const fetchProfilePicture = async () => {
            const accessToken = localStorage.getItem("userToken");
            if (!accessToken) {
                profilePictureUrl.value = blankProfilePicture;
                return;
            }
            const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
            try {
                const response = await axios.get(`http://127.0.0.1:5000/profilePicture/${userId}`, {
                    headers: { Authorization: `Bearer ${accessToken}` }
                });
                if (response.data && response.status === 200) {
                    profilePictureUrl.value = response.request.responseURL;
                }
                else {
                    profilePictureUrl.value = blankProfilePicture;
                }
            }
            catch (error) {
                profilePictureUrl.value = blankProfilePicture;
            }
        };
        const fetchUsername = async () => {
            const accessToken = localStorage.getItem("userToken");
            console.log(accessToken);
            const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
            console.log(userId);
            if (accessToken) {
                try {
                    const response = await axios.get(`http://127.0.0.1:5000/fetchUsername/${userId}`, {
                        headers: { Authorization: `Bearer ${accessToken}` }
                    });
                    username.value = response.data.username;
                    projects.value = response.data.projects;
                }
                catch (error) {
                    username.value = "Error loading username";
                    projects.value = [];
                    console.error("Error:", error);
                }
                await fetchProfilePicture();
                //await fetchProjects();
            }
            else {
                username.value = "Not logged in";
                projects.value = [];
            }
        };
        const fetchProjects = async () => {
            const accessToken = localStorage.getItem("userToken");
            const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
            if (!accessToken)
                return;
            try {
                const response = await axios.get(`http://127.0.0.1:5000/getProjects/${userId}`, {
                    headers: { Authorization: `Bearer ${accessToken}` }
                });
                projects.value = response.data;
                console.log(JSON.stringify(projects.value));
            }
            catch (error) {
                console.error("Error fetching projects:", error);
            }
        };
        const uploadProfilePicture = async (file) => {
            if (!file)
                return;
            const formData = new FormData();
            formData.append("file", file);
            const accessToken = localStorage.getItem("userToken");
            try {
                await axios.post("http://127.0.0.1:5000/uploadProfilePicture", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                        Authorization: `Bearer ${accessToken}`
                    }
                });
                await fetchProfilePicture();
            }
            catch (error) {
                console.error("Upload Error:", error);
            }
        };
        onMounted(async () => {
            await fetchUsername();
        });
        const addProject = () => {
          let max = projects.value.length > 0 ? projects.value.reduce((max, proj) => (parseInt(proj.id) > max ? parseInt(proj.id) : max), parseInt(projects.value[0].id)) : 0;
          const newProject = {
              id: max + 1,
              title: newProjectTitle.value,
              description: newProjectDescription.value,
              genres: selectedGenres.value.join(','),
              instruments: selectedInstruments.value.join(',')
          };
          projects.value.push(newProject);
          newProjectTitle.value = "";
          newProjectDescription.value = "";
          selectedGenres.value = [];
          showAddProjectPopup.value = false;
          selectedInstruments.value = [];
          addProjectToDB(newProject);
        };
        const addProjectToDB = async (project) => {
          const accessToken = localStorage.getItem("userToken");
          const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
          try {
              await axios.post(`http://127.0.0.1:5000/addProject/${userId}`, project, {
                  headers: {
                      Authorization: `Bearer ${accessToken}`
                  }
              });
              console.log("Project added successfully");
          }
          catch (error) {
              console.error("Error adding project:", error);
          }
        };
        const clickProject = async (project) => {
            try {
                router.push({ name: "ProjectView", params: { title: project.title } });
                console.log("Project opened successfully");
            }
            catch (error) {
                console.error("Error adding project:", error);
            }
        };

        const handleSelectedInstrumentsUpdate = async (updatedSelectedOptions) => {
            selectedInstruments.value = updatedSelectedOptions;
        }

        const handleSelectedGenresUpdate = async (updatedSelectedOptions) => {
            selectedGenres.value = updatedSelectedOptions;
        }
    const deleteProject = async (project) => {
      // Confirm deletion
      if (
        !confirm(
          `Are you sure you want to delete the project "${project.title}"?`
        )
      ) {
        return;
      }
      const accessToken = localStorage.getItem("userToken");
      const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
      try {
        // Use encodeURIComponent to safely encode the project title in the URL
        await axios.delete(
          `http://127.0.0.1:5000/deleteProject/${userId}/${encodeURIComponent(
            project.title
          )}`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );
        console.log("Project deleted successfully");
        await fetchUsername();
      } catch (error) {
        console.error("Error deleting the project:", error.response.data);
      }
    };
        return {
            username,
            projects,
            addProject,
            showAddProjectPopup,
            newProjectTitle,
            newProjectDescription,
            genres: genres,
            instruments: instruments,
            onClickFileInput,
            fileInput,
            profilePictureUrl,
            onMounted,
            uploadProfilePicture,
            clickProject,
            addProjectToDB,
            fetchUsername,
            selectedGenres,
            selectedInstruments,
            handleSelectedInstrumentsUpdate,
            handleSelectedGenresUpdate,
            deleteProject,
    };
    },
    components: { MultipleDropdown, HamburgerMenu }
};
</script>

<template>
  <!-- Fontawesome CDN Link -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
  <HamburgerMenu />
  <div class="profilePage">
    <div class="profileContainer">
      <button class="profile-picture" @click="onClickFileInput">
        <img
          :src="profilePictureUrl"
          alt="Profile Picture"
        />
        <div class="hover">
          <i class="fa-solid fa-pencil"></i>
          Change Profile Picture
        </div>
      </button>
      <input
        type="file"
        @change="uploadProfilePicture($event.target.files[0])"
        style="display: none"
        ref="fileInput"
      />
      <div class="profilePageStatsContainer">
        <h1>{{ username }}</h1>
      </div>
      <div class="projectGrid">
        <div v-if="showAddProjectPopup" class="addProjectPopup">
          <div class="popupContent">
            <h3>Add New Project</h3>
            <label for="projectTitle">Title:</label>
            <input
              type="text"
              id="projectTitle"
              v-model="newProjectTitle"
              style="
                border-radius: 5px;
                border: 2px dashed var(--colour-panel-hard);
              "
            />
            <label for="projectDescription">Description:</label>
            <textarea
              id="projectDescription"
              v-model="newProjectDescription"
              style="
                border-radius: 5px;
                border: 2px dashed var(--colour-panel-hard);
              "
            ></textarea>

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

            <div class="buttonContainer">
              <button @click="addProject">Add Project</button>
              <button @click="showAddProjectPopup = false">Cancel</button>
            </div>
          </div>
        </div>
        <div
          v-for="project in projects"
          :key="project.id"
          class="project"
          @click="clickProject(project)"
        >
          <button class="delete" @click.stop="deleteProject(project)">x</button>
          <h3>{{ project.title }}</h3>
          <p class="description">{{ project.description }}</p>
          <div class="tags">
            <p v-if="Array.isArray(project.genres) && project.genres.length > 0" v-for="genre in project.genres" class="genre">{{ genre }}</p>
            <p v-if="Array.isArray(project.instruments) && project.instruments.length > 0" v-for="instrument in project.instruments" class="genre">{{ instrument }}</p>
          </div>
        </div>
        <div class="project addProject" @click="showAddProjectPopup = true">
          <img src="../assets/New Project.svg"/>
          <p>Add Project</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profilePage {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.profileContainer {
  width: 70%;
  margin-top: 2em;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2em;
}

button.profile-picture {
  border-radius: 100%;
  max-width: 300px;
  height: 300px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0.1em 0.2em 0.05em var(--colour-dropshadow);
}
button.profile-picture img {
  display: block;
  overflow: hidden;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
button.profile-picture .hover {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 100%;
  color: var(--colour-background);
  background: var(--colour-text);
  opacity: 0%;
  transition: opacity 150ms;
  font-weight: 600;
}
button.profile-picture .hover:hover {
  opacity: 60%;
}
button.profile-picture .hover i {
  margin-right: 0.5em;
}


.profilePageStatsContainer {
  width: 100%;
  text-align: center;
}
.profilePageStatsContainer h1 {
  font-family: "Delta Gothic One";
  line-height: 0.8em;
  padding-bottom: 0.3em;
}

.projectGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: var(--colour-panel-hard);
  gap: 20px;
  width: 70%;
  margin-bottom: 2em;
}

.project {
  min-height: 150px;
  background-color: transparent;
  border-radius: 1em;
  border: 3px dashed var(--colour-panel-hard);
  display: grid;
  grid-template-rows: auto;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  --tag-colour: var(--colour-background);
  --tag-bg-colour: var(--colour-panel-hard);
  --delete-display: none;
  --svg-filter: invert(90%) sepia(97%) saturate(4765%) hue-rotate(212deg) brightness(84%) contrast(107%);
  text-align: center;
}
.project:hover {
  transform: scale(1.1);
  color: var(--colour-background);
  background-color: var(--colour-interactable-hover);
  border: none;
  --tag-colour: var(--colour-text);
  --tag-bg-colour: var(--colour-background);
  --delete-display: inherit;
  --svg-filter: none;
  transition: 0.2s ease-in;
}
.project button.delete {
  position: absolute;
  display: var(--delete-display);
  color: var(--colour-background);
  background-color: transparent;
  top: 0;
  width: 1.5em;
  height: 1.5em;
  font-size: 1.1em;
  line-height: 0.8em;
  padding-bottom: 0.2em;
  border-radius: 100%;
  font-family: "Fredoka";
  margin-bottom: auto;
}
.project button.delete:hover {
  color: var(--colour-interactable);
  background-color: var(--colour-background);
}

.project h3 {
  font-family: "Delta Gothic One";
  line-height: 1em;
  margin: 1.2em 0.25em 0 0.25em;
}
.project p.description {
  margin: 0.25em;
}

.project .tags {
  display: flex;
  justify-content: center;
  flex-flow: row wrap;
  gap: 0.25em;
  margin: 0 0.25em 0.25em 0.25em;
}
.project .tags p {
  padding: 0 0.25em 0 0.25em;
  border-radius: 0.25em;
  font-weight: 600;
  color: var(--tag-colour);
  background-color: var(--tag-bg-colour);
}

.addProject img {
  filter: var(--svg-filter);
}
.addProject p {
  font-weight: 600;
}
.addProject .plus {
  font-family: "Fredoka";
  font-size: 4em;
  line-height: 0.2em;
  padding-bottom: 0.26em;
}

.project img {
  width: 100%;
  height: 75px;
  object-fit: contain;
  margin: auto;
  display: block;
}
.popupContent {
  text-align: center;
  background-color: var(--colour-panel-soft);
  display: flex;
  border-radius: 10px;
  flex-direction: column;
}
.buttonContainer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  border: 3px var(--colour-panel-hard);
  padding: 0 10px;
}
.buttonContainer button:hover {
  background-color: var(--colour-interactable-hover);
}

select[multiple] option:checked {
  background-color: var(--selected-color);
  color: rgb(188, 26, 26);
}


@media (max-width: 900px) {
  .projectGrid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 550px) {
  .projectGrid {
    grid-template-columns: repeat(1, 1fr);
  }
}
</style>
