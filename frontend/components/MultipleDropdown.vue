<script>
export default {
  props: {
    options: {
      type: Array,
      required: true,
    },
    valueName: {
      type: String,
      required: true,
    },
    allowUpdates: {
      type: String,
      required: true,
    },
    alreadySelectedOptions: {
      type: Array,
    }
  },
  watch: {
    alreadySelectedOptions() {
      this.selectedOptions = this.alreadySelectedOptions ? this.alreadySelectedOptions : [];
    }
  },
  data() {
    return {
      isDropdownOpen: false,
      selectedOptions: this.alreadySelectedOptions ? this.alreadySelectedOptions : [],
    };
  },

  computed: {
    buttonText() {
      return this.selectedOptions.length > 0 ? `${this.valueName}: ${this.selectedOptions.join(', ')}` : `${this.valueName}`;
    }
  },
  methods: {
    toggleDropdown(event) {
      if (event.type == "blur" && !this.$el.contains(event.relatedTarget) ||
          event.type == "click")
      {
        this.$el.getElementsByTagName("ul")[0].style.zIndex = this.isDropdownOpen ? "1" : "10";
        this.isDropdownOpen = !this.isDropdownOpen;
      }
    },
    closeDropdown(event) {
      if (event.type == "blur" && !this.$el.contains(event.relatedTarget) ||
          event.type == "click")
      {
        this.$el.getElementsByTagName("ul")[0].style.zIndex = "1";
        this.isDropdownOpen = false;
      }
    },
    
    toggleOption(optionValue) {
      if (this.isDropdownOpen && this.allowUpdates == "True") {
        if (this.selectedOptions.includes(optionValue)) {
          this.selectedOptions = this.selectedOptions.filter(option => option !== optionValue);
        } else {
          this.selectedOptions.push(optionValue);
        }
        this.$emit('update:selectedOptions', this.selectedOptions);
      }
    },
    closeOption(optionValue) {
      if (this.selectedOptions.includes(optionValue)) {
        this.selectedOptions = this.selectedOptions.filter(option => option !== optionValue);
      } else {
        this.selectedOptions.push(optionValue);
      }
      this.$emit('update:selectedOptions', this.selectedOptions);
    }
  },
};
</script>


<template>
  <div class="multiple-dropdown">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">
    <button class="select-btn" @click="toggleDropdown" v-on:blur="closeDropdown"
      :style="{
        color: selectedOptions.length > 0 ? 'var(--dd-active-text-colour)':'var(--dd-text-colour)',
        backgroundColor: selectedOptions.length > 0 ? 'var(--dd-active-background-colour)':'var(--dd-background-colour)',
      }
    ">
      <span class="btn-text">{{ this.valueName }}</span>
      <span class="arrow-dwn">
        <i v-if="!isDropdownOpen" class="fa-solid fa-chevron-down"/>
        <i v-if="isDropdownOpen" class="fa-solid fa-chevron-up"/>
      </span>
    </button>
    <ul :style="{
      // maxHeight: this.isDropdownOpen ? '100vh' : '0vh',
      transform: this.isDropdownOpen ? 'scaleY(1)' : 'scaleY(0)',
      boxShadow: this.isDropdownOpen ? '0em 0.05em 0.5em 0.01em var(--colour-dropshadow)' : 'none',
    }">
      <button tabindex="0" v-for="(option, index) in options" :key="index" :value="option.value" 
        v-on:blur="closeDropdown"
        @click="toggleOption(option.value)" 
        :class="{ checked: selectedOptions.includes(option.value) }" 
        :style="{
          // maxHeight: this.isDropdownOpen ? '100%' : '0',
          cursor: this.isDropdownOpen ? 'pointer' : 'auto',
        }
      ">
        <i class="fa-solid fa-check check-icon"
          :style="{
            position: 'absolute',
            marginTop: '0.3em',
            color: this.isDropdownOpen && selectedOptions.includes(option.value) ? 'var(--dd-text-colour)' : '#00000000'
          }
        "/>
        <span class="item-text" :style="{
          color: this.isDropdownOpen ? 'var(--dd-text-colour)' : '#00000000'
        }">
          &#x2610 {{ option.label }}
        </span>
      </button>
    </ul>
  </div>
</template>

<style scoped>

.multiple-dropdown *{
  --dd-text-colour: var(--colour-text);
  --dd-button-background-colour: var(--colour-panel-soft);
  --dd-panel-background-colour: var(--colour-background);
  --dd-panel-dropshadow-colour: var(--colour-dropshadow);
  --dd-active-text-colour: var(--colour-background);
  --dd-active-background-colour: var(--colour-text);
  /* transition: all 1s, z-index 1ms, box-shadow 0.2s, color 0.2s; */
  
  transform-origin: top center;
  transition: transform 400ms, box-shadow 100ms;
}

.select-btn {
  padding: 0.25em 0.5em 0.25em 0.5em;
  line-height: 0;
  border-radius: 0.25em;
  transition: color 200ms, background-color 200ms;
}

.btn-text {
  margin-right: 0.25em;
}

.multiple-dropdown ul {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: var(--dd-panel-background-colour);
  position: absolute;
  min-width: 8em;
  padding: 0 0.5em 0 0.5em;
  border-radius: 0.25em;
  z-index: 1;
}

.multiple-dropdown ul * {
  transition: all 700ms;
  width: 100%;
  text-align: left;
}

.multiple-dropdown ul i {
  transition: color 200ms;
}
</style>