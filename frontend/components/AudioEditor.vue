<script>

export default {
  props: {
    initOffset: {
      type: Number,
      required: true,
    },
    initFileLength: {
      type: Number,
      required: true,
    },
    
    initTrackLength: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isBeingDragged: false,
      initX: 0,

      // The time the track starts at, in seconds (float).
      offset: this.initOffset,
      oldOffset: this.initOffset,
      // The length of the track container, in seconds (float).
      trackLength: this.initTrackLength,
      // The length of the file, in seconds (float).
      fileLength: this.initFileLength,
    };
  },
  mounted() {
    window.addEventListener('mouseup', this.endDrag, { passive: true });
    window.addEventListener('mousemove', this.drag, { passive: true });
  },
  unmounted() {
    window.removeEventListener('mouseup', this.endDrag, { passive: true });
    window.removeEventListener('mousemove', this.drag, { passive: true });
  },
  methods: {
    startDrag(event) {
      this.isBeingDragged = true;
      this.initX = event.clientX;
    },
    drag(event) {
      if (this.isBeingDragged) {
        // 1 SECOND = 1EM //
        this.offset = Math.min(Math.max(
          this.toEM(event.clientX - this.initX) + this.oldOffset, 0
        ), this.trackLength - this.fileLength);
      }
    },
    endDrag(event) {
      if (this.isBeingDragged) {
        this.isBeingDragged = false;
        this.oldOffset = this.offset;

        // this.offset NOW HOLDS THE NEW START POS in seconds!
        // TODO: UPLOAD IT TO BACKEND.
      }
    },
    toEM(px) {
      return parseFloat(px / parseInt(window.getComputedStyle(this.$el).fontSize));
    }
  },
};
</script>

<template>
  <div class="editor">
    <div
      class="file"
      @mousedown="startDrag($event)"
    >
      hi!
    </div>
  </div>
</template>

<style scoped>
.editor {
  display: flex;
  min-width: v-bind(trackLength + "em");
}
.editor .file {
  /* 1 SECOND = 1 EM */
  margin: 1em 0 1em v-bind(offset + "em");
  width: v-bind(fileLength + "em");
  color: var(--colour-background);
  background-color: var(--colour-interactable);
  border-radius: 0.5em;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
</style>