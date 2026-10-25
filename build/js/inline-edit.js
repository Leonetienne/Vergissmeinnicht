import Alpine from "alpinejs";

Alpine.data("inlineEdit", (get, set) => ({
  editing: false,
  draft: "",
  get value() {
    return get();
  },
  start() {
    this.draft = get();
    this.editing = true;
    setTimeout(() => {
      this.$refs.input.focus();
      this.$refs.input.select();
    });
  },
  commit() {
    if (!this.editing) return;
    this.editing = false;
    const value = this.draft.trim();
    if (value && value !== get()) set(value);
  },
  cancel() {
    this.editing = false;
  },
}));
