<script>
import { ref } from "vue";

export default {
  name: "App",
  setup() {
    const email = ref("");
    const password = ref("");
    const username = ref("");
    const dateOfBirth = ref(null);
    const menu = ref(false);

    const submitForm = () => {
      console.log("Email:", email.value);
      console.log("Password:", password.value);
      console.log("Username:", username.value);
      console.log("Date of Birth:", dateOfBirth.value);
    };

    return {
      email,
      password,
      username,
      dateOfBirth,
      menu,
      submitForm,
    };
  },
};
</script>

<template>
  <div class="signUpHomepage">
    <div class="signUpHeader">
      <h1>Sign up to Musi<span>C</span>ollab!</h1>
    </div>
    <div class="signUpContainer">
      <v-responsive class="formContainer">
        <v-text-field
          v-model="email"
          class="text-field-custom"
          label="Email address"
          placeholder="johndoe@gmail.com"
          type="email"
          variant="outlined"
          style="padding: 10px"
        ></v-text-field>
        <v-text-field
          v-model="password"
          class="text-field-custom"
          label="Password"
          placeholder="*******"
          type="password"
          variant="outlined"
          style="padding: 10px"
        ></v-text-field>
        <v-text-field
          v-model="username"
          class="text-field-custom"
          label="Username"
          placeholder="username123"
          type="text"
          variant="outlined"
          style="padding: 10px"
        ></v-text-field>
        <v-menu
          ref="menu"
          v-model="menu"
          :close-on-content-click="false"
          :nudge-right="40"
          transition="scale-transition"
          offset-y
          min-width="auto"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-text-field
              v-model="dateOfBirth"
              label="Date of Birth"
              placeholder="YYYY-MM-DD"
              readonly
              v-bind="attrs"
              v-on="on"
              outlined
              dense
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="dateOfBirth"
            @input="menu = false"
            style="
              position: relative;
              justify-content: center;
              align-items: center;
              left: 500px;
            "
          ></v-date-picker>
        </v-menu>
        <v-btn @click="submitForm" style="cursor: pointer; left: 50px"
          >Submit</v-btn
        >
      </v-responsive>
    </div>
    <RouterView />
  </div>
</template>

<style scoped>
.signUpHomepage {
  width: 100%;
  min-height: 100%;
}
.signUpHeader {
  text-align: center;
  height: 100px;
}

.signUpHeader h1 {
  position: relative;
  top: 50%;
  transform: translateY(-50%);
}
.signUpContainer {
  color: #ffffff;
  margin-top: 20px;
}
.formContainer {
  width: 60%;
  left: 20%;
  min-height: 50%;
  box-sizing: border-box;
}
</style>
