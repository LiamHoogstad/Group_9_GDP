<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import blankProfilePicture from "../assets/blankProfilePicture.png";
import { useRouter } from "vue-router";
import { genres, instruments } from '../assets/globalVariables.js';
import MultipleDropdown from "../components/MultipleDropdown.vue";

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
        };
    },
    components: { MultipleDropdown }
};
</script>

<template>
  <!-- Fontawesome CDN Link -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
  <div class="profilePage">
    <div class="profileContainer">
      <div class="profilePictureContainer">
        <img
          :src="profilePictureUrl"
          alt="Profile Picture"
          class="profilePicture"
        />
        <input
          type="file"
          @change="uploadProfilePicture($event.target.files[0])"
          style="display: none"
          ref="fileInput"
        />
        <v-btn @click="onClickFileInput">Change Profile Picture</v-btn>
      </div>
      <div class="profilePageStatsContainer">
        <h1>{{ username }}</h1>
      </div>
      <div class="separatorBar"></div>
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
          <h3>{{ project.title }}</h3>
          <p>{{ project.description }}</p>
          <p v-if="Array.isArray(project.genres) && project.genres.length > 0" class="genre">Genres: {{ project.genres.join(', ')}}</p>
          <p v-if="Array.isArray(project.instruments) && project.instruments.length > 0" class="genre">Instruments: {{ project.instruments.join(', ') }}</p>
        </div>
        <div class="project addProject" @click="showAddProjectPopup = true">
          <h3>
            <span><img src="../assets/addFolder.png" alt="" /></span>
          </h3>
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
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.profilePictureContainer {
  width: 100%;
  max-width: 300px;
  text-align: center;
  margin-bottom: 20px;
}

.profilePictureContainer button {
  padding: 10px 20px;
  margin-top: 20px;
}

.profilePicture {
  width: 100%;
  max-width: 300px;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.profilePictureContainer img {
  max-width: 100%;
  max-height: 100%;
  border-radius: 50%;
}

.profilePageStatsContainer {
  width: 100%;
  text-align: center;
}
.separatorBar {
  height: 5px;
  width: 70%;
  margin: 20px 0;
}

.projectGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border: var(--colour-panel-hard);
  gap: 20px;
  width: 70%;
}

.project {
  min-height: 150px;
  background-color: transparent;
  border-radius: 10px;
  border: 3px dashed var(--colour-panel-hard);
  display: grid;
  grid-template-rows: repeat(2, 1fr);
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.project:hover {
  transform: scale(1.1);
  background-color: var(--colour-interactable-hover);
  transition: 0.2s ease-in-out;
}
.project h3,
.project p {
  text-align: center;
}

.addProject {
  background-color: var(--colour-panel-hard);
  cursor: pointer;
}

.addProject span {
  font-size: 24px;
  background-color: var(--colour-panel-soft);
  color: var(--colour-text);
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
</style>
