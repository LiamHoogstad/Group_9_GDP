<script>
import { ref, computed } from "vue";
import axios from "axios";

export default {
  name: "LandingPage",

  setup() {
    return {};
  },
};
</script>

<template>
  <div class="landingPage">
    <div class="boundingBox">
      <h1>Welcome to MusiCollab!</h1>
    <p>
      If you have an account,
      <router-link to="/sign-in">sign in here</router-link>.
    </p>
    <p>Alternatively, <router-link to="/sign-up">sign up here</router-link>.</p>
    </div>
  </div>
</template>

<style scoped>
.landingPage {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background-color: var(--colour-panel-soft);
}

.landingPage .boundingBox {
  padding: 2em;
  border-radius: 3em;
  background-color: var(--colour-background);
  box-shadow: 0 0 2em var(--colour-dropshadow);
}

.boundingBox h1 {
  font-family: 'Delta Gothic One';
  margin: 0.5em;
}

.boundingBox p {
  margin-bottom: 0.7em;
}
</style>
