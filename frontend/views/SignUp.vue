<script>
import { ref, computed } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

export default {
  name: "SignUp",

  setup() {
    const email = ref("");
    const password = ref("");
    const username = ref("");
    const dateOfBirth = ref(null);
    const userAge = ref("---");
    const menu = ref(false);
    const router = useRouter();

    const emailError = ref("");
    const passwordError = ref("");
    const usernameError = ref("");
    const dateOfBirthError = ref("");

    const validateEmail = async () => {
      const emailRegex = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/g;
      if (!emailRegex.test(email.value)) {
        emailError.value = "Invalid email format (e.g., johndoe@example.com).";
        return false;
      } else {
        try {
          const response = await axios.post(
            "http://127.0.0.1:5000/checkEmail",
            {
              email: email.value,
            }
          );

          if (!response.data.isAvailable) {
            emailError.value = "Email is not available";
            return false;
          } else {
            emailError.value = "";
            return true;
          }
        } catch (error) {
          console.error("Error checking email:", error);
          emailError.value = "Error checking email availability";
          return false;
        }
      }
    };

    const validatePassword = () => {
      const passwordValue = password.value;
      const specialCharacterRegex = /[!@#$%^&*(),.?":{}|<>]/;
      const uppercaseRegex = /[A-Z]/;
      const numberRegex = /[0-9]/;

      if (
        passwordValue.length < 8 ||
        !specialCharacterRegex.test(passwordValue) ||
        !uppercaseRegex.test(passwordValue) ||
        !numberRegex.test(passwordValue)
      ) {
        passwordError.value =
          "Password must be at least 8 characters,at least one special character,at least one uppercase letter and at least one number.";
        return false;
      } else {
        passwordError.value = "";
        return true;
      }
    };

    const validateUsername = async () => {
      if (username.value.length < 3) {
        usernameError.value = "Username must be at least 3 characters.";
        return false;
      } else {
        try {
          const response = await axios.post(
            "http://127.0.0.1:5000/checkUsername",
            {
              username: username.value,
            }
          );

          if (!response.data.isAvailable) {
            usernameError.value = "Username is not available";
            return false;
          } else {
            usernameError.value = "";
            return true;
          }
        } catch (error) {
          console.error("Error checking username:", error);
          usernameError.value = "Error checking username availability";
          return false;
        }
      }
    };

    const validateAge = () => {
      if (dateOfBirth.value) {
        const today = new Date();
        const birthDate = new Date(dateOfBirth.value);
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
          age--;
        }
        userAge.value = age;
        if (age < 18) {
          dateOfBirthError.value = "You must be over 18.";
          return false;
        } else {
          dateOfBirthError.value = "";
          return true;
        }
      }
      return true;
    };

    const canSubmit = computed(() => {
      return (
        email.value.trim() !== "" &&
        password.value.trim() !== "" &&
        username.value.trim() !== "" &&
        dateOfBirth.value !== null &&
        emailError.value === "" &&
        passwordError.value === "" &&
        usernameError.value === "" &&
        dateOfBirthError.value === ""
      );
    });
    // Form submission
    const submitForm = async () => {
      const isEmailValid = await validateEmail();
      const isPasswordValid = validatePassword();
      const isUsernameValid = validateUsername();
      const isAgeValid = validateAge();

      if (isEmailValid && isPasswordValid && isUsernameValid && isAgeValid) {
        try {
          const formData = {
            email: email.value,
            password: password.value,
            username: username.value,
            dateOfBirth: dateOfBirth.value,
          };
          const response = await axios.post(
            "http://127.0.0.1:5000/submit",
            formData
          );
          if (response.data.success) {
            console.log("Sign Up Successful");
            localStorage.setItem("userToken", response.data.access_token);
            console.log("userToken:", response.data.access_token);
            router.push({ name: "ProfilePage" });
          }
        } catch (error) {
          console.error(error);
        }
      }
    };

    return {
      email,
      password,
      username,
      dateOfBirth,
      userAge,
      menu,
      submitForm,
      emailError,
      passwordError,
      usernameError,
      dateOfBirthError,
      validateEmail,
      validatePassword,
      validateUsername,
      validateAge,
      canSubmit,
    };
  },
};
</script>

<template>
  <div class="signUpHomepage">
    <div class="signUpHeader">
      <h1>Sign up to Musi<span>C</span>ollab!</h1>
    </div>
    <div class="signInOption">
      <p>
        Already have an account?
        <router-link to="/sign-in">sign in here</router-link>.
      </p>
    </div>
    <div class="signUpContainer">
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
          @blur="validateEmail"
        ></v-text-field>
        <v-text-field
          v-model="password"
          :error-messages="passwordError"
          class="text-field-custom"
          label="Password"
          placeholder="*******"
          type="password"
          variant="outlined"
          style="padding: 10px"
          @blur="validatePassword"
        ></v-text-field>
        <v-text-field
          v-model="username"
          :error-messages="usernameError"
          class="text-field-custom"
          label="Username"
          placeholder="username123"
          type="text"
          variant="outlined"
          style="padding: 10px"
          @blur="validateUsername"
        ></v-text-field>
        <p>Please select your Date Of Birth below:</p>
        <div class="datepick">
          <v-date-picker
            show-adjacent-months
            v-model="dateOfBirth"
            @change="validateAge"
            @click="validateAge"
          ></v-date-picker>
        </div>
        <v-text-field
          v-model="dateOfBirth"
          :error-messages="dateOfBirthError"
          label="Date of Birth"
          placeholder="YYYY-MM-DD"
          readonly
          outlined
          dense
          style="padding-top: 20px"
          @change="validateAge"
        ></v-text-field>
        <p>
          You are, <span>{{ userAge }}</span> years old
        </p>
        <div class="submitButtonContainer">
          <v-btn
            :disabled="!canSubmit"
            @click="submitForm"
            style="cursor: pointer"
            >Submit</v-btn
          >
        </div>
      </v-responsive>
    </div>
    <router-view />
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
.submitButtonContainer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
.signUpContainer p span {
  font-weight: bolder;
  font-size: larger;
}
.signInOption {
  text-align: center;
}
</style>
