import Alpine from "alpinejs";

Alpine.data("inlineEdit", (get, set, { allowEmpty = false } = {}) => ({
  editing: false,
  draft: "",
  get value() {
    return get();
  },
  start() {
    this.draft = get();
    this.editing = true;
    // x-show reveals the input in an animation frame, so focus and measure in the next one
    setTimeout(() => requestAnimationFrame(() => {
      this.$refs.input.focus();
      this.$refs.input.select();
      this.fit();
    }));
  },
  fit() {
    const input = this.$refs.input;
    if (input.tagName !== "TEXTAREA") return;
    input.style.height = "auto";
    input.style.height = `${input.scrollHeight + input.offsetHeight - input.clientHeight}px`;
  },
  commit() {
    if (!this.editing) return;
    this.editing = false;
    const value = this.draft.trim();
    if ((value || allowEmpty) && value !== get()) set(value);
  },
  cancel() {
    this.editing = false;
  },
}));
