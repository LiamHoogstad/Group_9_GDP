<template>
  <input
    ref="input"
    v-model="currentValue"
    type="range"
    :min="min"
    :max="max"
    class="slider"
    @input="onInput"
  />
</template>

<script>
export default {
  props: {
    value: {
      type: Number,
      required: true,
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
      currentValue: this.value,
    };
  },
  watch: {
    value(newValue) {
      this.currentValue = newValue;
    },
  },
  methods: {
    onInput() {
      this.$emit("update:modelValue", parseInt(this.currentValue));
    },
  },
};
</script>

<style scoped>
.slider {
  --slider-height: 1.2em;
  --track-height: 0.4em;
  border-radius: var(--slider-height);
  height: var(--slider-height);
  width: inherit;
  appearance: none;
  overflow: hidden;
  background-color: var(
    --colour-background
  ); /* Non-gradient background for old browsers */
}

.slider::-webkit-slider-runnable-track {
  height: var(--track-height);
  border-radius: var(--slider-height);
  background: var(--colour-interactable);
  background-image: linear-gradient(
    90deg,
    var(--colour-background) calc(var(--slider-height) * 0.4),
    var(--colour-interest) calc(var(--slider-height) * 0.6),
    var(--colour-interactable) calc(100% - (var(--slider-height) * 0.6)),
    var(--colour-background) calc(100% - (var(--slider-height) * 0.4))
  );
}
.slider::-moz-range-track {
  height: var(--track-height);
  width: calc(100% - var(--track-height) * 2);
  border-radius: var(--slider-height);
  background: var(--colour-interactable);
  background-image: linear-gradient(
    90deg,
    var(--colour-interest),
    var(--colour-interactable)
  );
}

.slider::-webkit-slider-thumb {
  margin-top: calc((var(--slider-height) - var(--track-height)) * -0.5);
  -webkit-appearance: none;
  -webkit-box-sizing: border-box;
  background-color: var(--colour-background);
  box-shadow: calc(100vw + (var(--slider-height) / 2)) 0 0 100vw
    var(--colour-background);
  height: var(--slider-height);
  width: var(--slider-height);
  border-radius: var(--slider-height);
  border: calc((var(--slider-height) - var(--track-height)) / 2) solid
    var(--colour-interactable);
  cursor: pointer;
}
.slider::-moz-range-thumb {
  -moz-appearance: none;
  -moz-box-sizing: border-box;
  background-color: var(--colour-background);
  box-shadow: calc(100vw + (var(--slider-height) / 2)) 0 0 100vw
    var(--colour-background);
  height: var(--slider-height);
  width: var(--slider-height);
  border-radius: var(--slider-height);
  border: calc((var(--slider-height) - var(--track-height)) / 2) solid
    var(--colour-interactable);
  cursor: pointer;
}
</style>
