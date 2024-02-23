import "./assets/main.css";

// main.js
import { createApp } from "vue";
import App from "./App.vue"; // This import should be at the top

// Vuetify
import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css"; // Import Material Design Icons
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import router from "./router";

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    iconfont: "mdi", // Specify the iconfont to use, 'mdi' in this case
  },
});

const app = createApp(App);

app.use(vuetify);
app.use(router);

app.mount("#app");
