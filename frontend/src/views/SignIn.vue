<script>
import { ref, computed } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  name: "SignIn",
  setup() {
    const router = useRouter();
    const email = ref("");
    const password = ref("");
    const emailError = ref("");
    const passwordError = ref("");
    const loginError = ref("");

    const validateEmailForLogin = async () => {
      const emailRegex = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;
      if (!emailRegex.test(email.value)) {
        emailError.value = "Invalid email format (e.g., johndoe@example.com).";
        return false;
      } else {
        try {
          const response = await axios.post(
            "http://localhost:5000/checkEmailForLogin",
            {
              email: email.value,
            }
          );

          if (!response.data.exists) {
            emailError.value = "No account found with that email.";
            return false;
          } else {
            emailError.value = "";
            return true;
          }
        } catch (error) {
          console.error("Error checking email:", error);
          emailError.value = "Error during the login process";
          return false;
        }
      }
    };

    const validatePassword = async () => {
      if (password.value === "") {
        passwordError.value = "";
        return false;
      } else {
        return true;
      }
    };

    function goToProfile() {
      router.push({ name: "ProfilePage" });
    }
    const canSubmit = computed(() => {
      return email.value.trim() !== "" && password.value.trim() !== "";
    });

    const submitForm = async () => {
      const isEmailValid = await validateEmailForLogin();
      const isPasswordValid = validatePassword();
      loginError.value = "";

      if (isEmailValid && isPasswordValid) {
        try {
          const formData = {
            email: email.value,
            password: password.value,
          };
          const response = await axios.post(
            "http://localhost:5000/login",
            formData
          );
          if (response.data.successful) {
            console.log("Login successful");
            router.push({ name: "ProfilePage" });
          } else {
            loginError.value =
              "Login failed. Please check your email and password.";
          }
        } catch (error) {
          loginError.value = "There was an error processing your request.";
        }
      } else {
        loginError.value = "Email or password validation failed.";
      }
    };

    return {
      goToProfile,
      email,
      emailError,
      passwordError,
      password,
      validateEmailForLogin,
      validatePassword,
      submitForm,
      canSubmit,
      loginError,
    };
  },
};
</script>

<template>
  <div class="signInHomepage">
    <div class="signInHeader">
      <h1>Sign In to MusiCollab</h1>
    </div>
    <div class="signUpOption">
      <p>
        Don't have an account?
        <router-link to="/sign-up">sign up here</router-link>.
      </p>
    </div>
    <div class="signInContainer">
      <v-responsive class="formContainer">
        <v-text-field
          v-model="email"
          :error-messages="emailError"
          class="text-field-custom"
          label="Email address"
          placeholder="johndoe@gmail.com"
          type="email"
          variant="outlined"
          style="padding: 10px"
          @blur="validateEmailForLogin"
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
        <div class="submitButtonContainer">
          <v-btn
            :disabled="!canSubmit"
            @click="submitForm"
            style="cursor: pointer"
            >Submit</v-btn
          >
        </div>
        <div class="loginErrorMessage">
          <p v-if="loginError !== null">{{ loginError }}</p>
        </div>
      </v-responsive>
    </div>
  </div>
</template>

<style scoped>
.signInHomepage {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100vh;
}
.signInHeader {
  text-align: center;
  padding: 20px;
}
.signUpOption {
  text-align: center;
  padding-bottom: 10px;
}
.signInContainer {
  position: relative;
  width: 50%;
  left: 25%;
  min-height: 60%;
}
.submitButtonContainer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
.loginErrorMessage {
  text-align: center;
  color: red;
}
</style>
