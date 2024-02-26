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
    <h1>Welcome to MusiCollab!</h1>
    <p>
      If you have an account,
      <router-link to="/sign-in">sign in here</router-link>.
    </p>
    <p>Alternatively, <router-link to="/sign-up">sign up here</router-link>.</p>
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
}

.landingPage h1 {
  margin-bottom: 20px;
}

.landingPage p {
  margin-bottom: 10px;
}
</style>
