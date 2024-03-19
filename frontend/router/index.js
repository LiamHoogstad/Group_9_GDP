import { createRouter, createWebHistory } from "vue-router";
import ProfilePage from "../views/ProfilePage.vue";
import SignIn from "../views/SignIn.vue";
import SignUp from "../views/SignUp.vue";
import LandingPage from "../views/LandingPage.vue";
import ExplorePage from "../views/ExplorePage.vue";
import ProjectView from "../views/ProjectView.vue"

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
      path: "/explore",
      name: "ExplorePage",
      component: ExplorePage,
    },
    {
      path: "/profile-page",
      name: "ProfilePage",
      component: ProfilePage,
    },
    {
      path: '/profile-page/:title',
    name: 'ProjectView',
    component: ProjectView,
  },
  ],
});

export default router;
