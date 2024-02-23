<template>
  <input ref="input" v-model="currentValue" type="range" :min="min" :max="max" class="slider" @input="onInput"/>
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      required: true
    },
    min: {
      type: Number,
      required: true,
    },
    max: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      currentValue: this.value
    };
  },
  methods: {
    onInput() {
      this.$emit('input', parseInt(this.currentValue));
    }
  }
};
</script>

<style scoped>

.slider {
  -webkit-appearance: none;
  -moz-appearance: none;
  --slider-height: 1.2em;
  appearance: none;
  border-radius: 1em;
  height: var(--slider-height);
  width: inherit;
  background-color: var(--colour-background); /* Non-gradient background for old browsers */
}

.slider::-webkit-slider-runnable-track {
  height: 0.4em;
  border-radius: var(--slider-height);
  background: var(--colour-interactable);
  background-image: linear-gradient(.25turn, var(--colour-interest), var(--colour-interactable));
}
.slider::-moz-range-track {
  height: 0.4em;
  width: calc(100% - 1em);
  border-radius: var(--slider-height);
  background: var(--colour-interactable);
  background-image: linear-gradient(.25turn, var(--colour-interest), var(--colour-interactable));
}

.slider::-webkit-slider-thumb {
  margin-top: calc(var(--slider-height) * -0.3);
  -webkit-appearance: none;
  background-color: var(--colour-background);
  height: var(--slider-height);
  width: var(--slider-height);
  border-radius: var(--slider-height);
  border: calc(var(--slider-height) * 0.33) solid var(--colour-interactable);
  cursor: pointer;
}
.slider::-moz-range-thumb {
  background-color: var(--colour-background);
  height: calc(var(--slider-height) * 0.4);
  width: calc(var(--slider-height) * 0.4);
  border-radius: var(--slider-height);
  border: calc(var(--slider-height) * 0.33) solid var(--colour-interactable);
  cursor: pointer;
}

</style>