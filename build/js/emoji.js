import Alpine from "alpinejs";

let emojiList = null;

async function loadEmoji() {
  if (!emojiList) {
    const response = await fetch(document.body.dataset.emojiUrl);
    const data = await response.json();
    emojiList = Object.entries(data).map(([char, info]) => ({ char, name: info.name }));
  }
  return emojiList;
}

Alpine.data("emojiControl", (get, set) => ({
  open: false,
  loaded: false,
  query: "",
  all: [],
  get value() {
    return get();
  },
  get results() {
    const q = this.query.trim().toLowerCase();
    return q ? this.all.filter((e) => e.name.includes(q)) : this.all;
  },
  async toggle() {
    this.open = !this.open;
    if (!this.open) return;
    this.query = "";
    setTimeout(() => this.$refs.search.focus());
    this.all = await loadEmoji();
    this.loaded = true;
  },
  close() {
    this.open = false;
  },
  pick(char) {
    this.open = false;
    if (char !== get()) set(char);
  },
}));
