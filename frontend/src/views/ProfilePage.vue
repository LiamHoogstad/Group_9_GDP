<script>
import { ref, onMounted } from "vue";
import axios from "axios";
import blankProfilePicture from "../assets/blankProfilePicture.png";

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

    const onClickFileInput = () => fileInput.value.click();

    const fetchProfilePicture = async () => {
      const accessToken = localStorage.getItem("userToken");
      if (!accessToken) {
        profilePictureUrl.value = blankProfilePicture;
        return;
      }
      const userId = JSON.parse(atob(accessToken.split(".")[1])).sub;
      try {
        const response = await axios.get(
          `http://localhost:5000/profilePicture/${userId}`,
          {
            headers: { Authorization: `Bearer ${accessToken}` },
          }
        );
        if (response.data && response.status === 200) {
          profilePictureUrl.value = response.request.responseURL;
        } else {
          profilePictureUrl.value = blankProfilePicture;
        }
      } catch (error) {
        console.error("Error fetching profile picture:", error);
        profilePictureUrl.value = blankProfilePicture;
      }
    };

    const uploadProfilePicture = async (file) => {
      if (!file) return;
      const formData = new FormData();
      formData.append("file", file);
      const accessToken = localStorage.getItem("userToken");
      try {
        await axios.post(
          "http://localhost:5000/uploadProfilePicture",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );
        await fetchProfilePicture();
      } catch (error) {
        console.error("Upload Error:", error);
      }
    };

    onMounted(async () => {
      const accessToken = localStorage.getItem("userToken");
      if (accessToken) {
        try {
          const response = await axios.get("http://localhost:5000/protected", {
            headers: { Authorization: `Bearer ${accessToken}` },
          });
          username.value = response.data.username;
        } catch (error) {
          username.value = "Error loading username";
          console.error("Error:", error);
        }
        await fetchProfilePicture();
        await fetchProjects();
      } else {
        username.value = "Not logged in";
      }
    });

    const addProject = () => {
      const newProject = {
        id: projects.value.length + 1,
        title: newProjectTitle.value,
        description: newProjectDescription.value,
      };
      projects.value.push(newProject);
      newProjectTitle.value = "";
      newProjectDescription.value = "";
      showAddProjectPopup.value = false;

      addProjectToDB(newProject);
    };
    const addProjectToDB = async (project) => {
      const accessToken = localStorage.getItem("userToken");
      try {
        await axios.post("http://localhost:5000/addProject", project, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        console.log("Project added successfully");
      } catch (error) {
        console.error("Error adding project:", error);
      }
    };

    const fetchProjects = async () => {
      const accessToken = localStorage.getItem("userToken");
      if (!accessToken) return;
      try {
        const response = await axios.get("http://localhost:5000/getProjects", {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        projects.value = response.data;
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    };
    return {
      username,
      projects,
      addProject,
      showAddProjectPopup,
      newProjectTitle,
      newProjectDescription,
      onClickFileInput,
      fileInput,
      profilePictureUrl,
      onMounted,
      uploadProfilePicture,
      addProjectToDB,
    };
  },
};
</script>

<template>
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
            <input type="text" id="projectTitle" v-model="newProjectTitle" />
            <label for="projectDescription">Description:</label>
            <textarea
              id="projectDescription"
              v-model="newProjectDescription"
            ></textarea>
            <div class="buttonContainer">
              <button @click="addProject">Add Project</button>
              <button @click="showAddProjectPopup = false">Cancel</button>
            </div>
          </div>
        </div>
        <div v-for="project in projects" :key="project.id" class="project">
          <h3>{{ project.title }}</h3>
          <p>{{ project.description }}</p>
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
  transform: rotateX(180deg);
}

.profilePageStatsContainer {
  width: 100%;
  text-align: center;
}
.separatorBar {
  height: 5px;
  background-color: white;
  width: 70%;
  margin: 20px 0;
}

.projectGrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  width: 70%;
}

.project {
  min-height: 150px;
  background-color: transparent;
  border: 3px solid white;
  border-radius: 10px;
  display: grid;
  grid-template-rows: repeat(2, 1fr);
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.project:hover {
  transform: scale(1.1);
  transition: 0.2s ease-in-out;
}
.project h3,
.project p {
  text-align: center;
}

.addProject {
  background-color: transparent;
  border: 2px dashed transparent;
  cursor: pointer;
}

.addProject span {
  font-size: 24px;
  color: white;
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
  display: flex;
  flex-direction: column;
}
.buttonContainer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
}
.buttonContainer button:hover {
  color: gray;
}
</style>
