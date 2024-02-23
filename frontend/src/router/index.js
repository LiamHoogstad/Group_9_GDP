import { createRouter, createWebHistory } from "vue-router";
import ProfilePage from "../views/ProfilePage.vue";
import SignIn from "../views/SignIn.vue";
import SignUp from "../views/SignUp.vue";
import LandingPage from "../views/LandingPage.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "LandingPage",
      component: LandingPage,
    },
    {
      path: "/sign-in",
      name: "SignIn",
      component: SignIn,
    },
    {
      path: "/sign-up",
      name: "SignUp",
      component: SignUp,
    },
    {
      path: "/profile-page",
      name: "ProfilePage",
      component: ProfilePage,
    },
  ],
});

export default router;
