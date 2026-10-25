import Alpine from "alpinejs";
import { op } from "./api";

const LIST_LABEL_MAX = 24;

Alpine.data("searchPopup", () => ({
  open: false,
  query: "",
  results: [],
  selected: 0,
  searched: false,
  globalKey(event) {
    if ((event.ctrlKey || event.metaKey) && !event.shiftKey && !event.altKey && event.key.toLowerCase() === "f") {
      event.preventDefault();
      this.show();
    }
  },
  show() {
    this.open = true;
    setTimeout(() => {
      this.$refs.input.focus();
      this.$refs.input.select();
    });
  },
  close() {
    this.open = false;
  },
  async fetch() {
    const q = this.query.trim();
    if (q.length < 2) {
      this.results = [];
      this.searched = false;
      return;
    }
    let data;
    try {
      data = await op("search", { q });
    } catch (error) {
      window.toast(error.message, { error: true });
      return;
    }
    if (q !== this.query.trim()) return;
    const where = (b) => (b.emoji ? b.emoji + " " : "") + b.name;
    this.results = [
      ...data.boards.map((b) => ({ key: "b" + b.id, label: where(b), where: "Board", tag: "", url: b.url })),
      ...data.tasks.map((t) => ({
        key: "t" + t.id,
        label: t.title,
        where: where(t.board) + (t.list.is_default || t.list.title.length > LIST_LABEL_MAX ? "" : ": " + t.list.title),
        tag: t.state === "open" ? "" : t.state,
        url: t.board.url + (t.state === "archived" ? "archive/" : "") + "#task-" + t.id,
      })),
    ];
    this.selected = 0;
    this.searched = true;
  },
  moveSel(step) {
    if (!this.results.length) return;
    this.selected = (this.selected + step + this.results.length) % this.results.length;
  },
  go(result) {
    if (!result) return;
    this.open = false;
    const target = new URL(result.url, location.href);
    const samePage = target.pathname === location.pathname;
    location.href = result.url;
    if (samePage && target.hash) location.reload();
  },
}));
