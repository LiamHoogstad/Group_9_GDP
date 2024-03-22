<script>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import HamburgerMenu from "../components/HamburgerMenu.vue";

export default {
    name: "ExplorePage",
    setup() {
        const projects = ref([]);
        const fetchAllProjects = async () => {
            try {
                const response = await axios.get(`http://127.0.0.1:5000/getAllProjects`);
                projects.value = response.data;
                console.log(JSON.stringify(projects.value));
            }
            catch (error) {
                console.error("Error fetching projects:", error);
            }
        };
        onMounted(() => {
            fetchAllProjects();
        });
        return {
            projects,
        };
    },
    components: { HamburgerMenu }
};
</script>

<template>
  <div class="explorePage">
    <header>
      <h1>Explore</h1>
      <HamburgerMenu/>
    </header>
    <ul>
      <div class="track" v-for="project in projects">
        <div class="info">
          <h3 class="title">{{ project.title }}</h3>
          <h3 class="creator">{{ project.user }}</h3>
        </div>
        <h3 class="description">{{ project.description }}</h3>
        <div class="likeDislike">
          <button class="like">like {{ 0 }}</button>
          <button>dislike {{ 0 }}</button>
        </div>
        <div class="audioPreview"></div>
        <button class="play">
          <img src="../assets/Play.svg"/>
        </button>
      </div>
    </ul>
  </div>
</template>

<style scoped>
.explorePage {
  height: 100vh;
  text-align: center;
}

header {
  background-color: var(--colour-panel-soft);
  padding: 0.6em 0.5em 1.15em 0.5em;
  margin-bottom: 1em;
}

h1 {
  font-family: 'Delta Gothic One';
  margin: 0;
  padding: 0;
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

.track .info .title{
  font-family: "Delta Gothic One";
}
.track .info .creator{
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

.track .likeDislike button{
  color: var(--colour-interactable);
  background-color: var(--colour-background);
  padding: 0 0.25em 0 0.25em;
  margin-left: 0.5em;
  border-radius: 0.25em;
}

.track .likeDislike button.like{
  margin-bottom: 0.5em;
}

.track .likeDislike button{
  color: var(--colour-interactable);
  background-color: var(--colour-background);
  font-weight: 600;
  padding: 0 0.25em 0 0.25em;
  border-radius: 0.25em;
}

.track .audioPreview {
  flex: 1
}

.track .play {
  margin-right: 0.5em;
}

</style>
