<script>
export default {
  data() {
    return {
      drawerVisible: false,
    };
  },
};
</script>


<template>
  <div class="buttonAndDrawer">
    <button id="hamburger" @click="drawerVisible = true">
      <img src="@/assets/Hamburger Menu.svg" />
    </button>
    <div id="drawer"
      :style="{
        width: drawerVisible ? '25em' : '0',
        paddingLeft: drawerVisible ? '10px' : '0',
      }"
    >
      <button class="close" @click="drawerVisible = false">x</button>
      <ul>
        <h1><router-link to="/profile-page">Account</router-link></h1>
        <h1><router-link to="/explore">Explore</router-link></h1>
        <h1><router-link to="/">Sign Out</router-link></h1>
      </ul>
    </div>
  </div>
</template>

<style scoped>

button#hamburger {
  position: absolute;
  top: 0;
  right: 0;
  margin: 0.4em 0 0 0;
  background-color: var(--colour-interactable);
  border-radius: 100% 0 0 100%;
  padding: 0.75em 1em 0.75em 1em;
  cursor: pointer;
}

button#hamburger img {
  width: 2em;
  height: 2em;
}

#drawer {
  position: absolute;
  overflow: hidden;
  text-align: right;
  top: 0;
  right: 0;
  width: 0;
  height: 100vh;
  border-radius: 2em 0 0 2em;
  color: var(--colour-background);
  background: var(--colour-interactable);
  font-family: "Delta Gothic One";
  transition: all 0.2s;
}

#drawer ul {
  list-style: none;
  text-align: center;
  margin-top: 0.75em;
}

#drawer a:link,
#drawer a:visited,
#drawer a:active {
  color: var(--colour-background);
  text-decoration: none;
  margin-bottom: 0.25em;
  width: fit-content;
}

#drawer button {
  box-shadow: none;
}

#drawer button.close {
  font-family: "Fredoka";
  font-size: 2.5em;
  min-width: 0;
  padding: 0 .5em 0 0.5em;
}

#drawer button.close:hover {
  background: none;
}
#drawer button.close:active {
  background: none;
}
</style>