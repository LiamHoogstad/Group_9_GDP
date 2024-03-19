<script>
import { ref, computed } from "vue";
import axios from "axios";

export default {
  name: "ExplorePage",

  setup() {
    return {};
  },
};
</script>

<template>
  <div class="explorePage">
    <h1>Explore</h1>
    <ul>
      <div class="track" v-for="index in 10">
        <div class="info">
          <h3 class="title">{{ "Title"}}</h3>
          <h3 class="creator">{{ "Creator"}}</h3>
        </div>
        <h3 class="description">{{ "Description text lorem ipsum etc." }}</h3>
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
  background-color: var(--colour-panel-soft);
}

h1 {
  font-family: 'Delta Gothic One';
  padding: 0.5em;
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