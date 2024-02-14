<script>
import { ref } from "vue";
import axios from "axios";

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
  methods: {
    async submitForm() {
      const formData = {
        email: this.email,
        password: this.password,
        username: this.username,
        dateOfBirth: this.dateOfBirth,
      };

      try {
        const response = await axios.post(
          "http://localhost:5000/submit",
          formData
        );
        console.log(response.data);
      } catch (error) {
        console.error(error);
      }
    },
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
        <p>Please select your Date Of Birth below:</p>
        <div class="datepick">
          <v-date-picker
            v-model="dateOfBirth"
            @input="menu = false"
          ></v-date-picker>
        </div>
        <v-text-field
          v-model="dateOfBirth"
          label="Date of Birth"
          placeholder="YYYY-MM-DD"
          readonly
          outlined
          dense
          style="padding-top: 20px"
        ></v-text-field>
        <div class="datepick">
          <v-btn @click="submitForm" style="cursor: pointer"> Submit </v-btn>
        </div>
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
.formContainer p {
  text-align: center;
}
.datepick {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 20px;
}
</style>
