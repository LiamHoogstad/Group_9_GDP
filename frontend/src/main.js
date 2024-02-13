import "./assets/main.css";

// main.js
import { createApp } from "vue";
import App from "./App.vue"; // This import should be at the top

// Vuetify
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import router from "./router";

const vuetify = createVuetify({
  components,
  directives,
});

createApp(App).use(vuetify).mount("#app");

app.use(router);

app.mount("#app");
