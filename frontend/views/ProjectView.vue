<script setup>
import { RouterLink, useRouter } from 'vue-router'
import Slider from '../components/Slider.vue'
const router = useRouter()
const title = router.currentRoute.value.params.title

</script>

<template>
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
      <button id="play_pause"><img src="@/assets/Play.svg"></button>
      <Slider id="master_volume"/>
    </div>
    <div class="right">
      <button id="hamburger"><img src="@/assets/Hamburger Menu.svg"></button>
    </div>
  </div>
</template>

<style scoped>

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
  font-family: 'Delta Gothic One';
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

#track_list .track{
  margin: 1em 0 0 1em;
  padding: 1em 1em 1em 2em;
  background-color: var(--colour-interactable);
  border-radius: 5em 0 0 5em;
}
</style>
