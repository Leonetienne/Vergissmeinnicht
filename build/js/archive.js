import Alpine from "alpinejs";
import { op } from "./api";
import { byPosition, page } from "./page";
import { failToast, formatDate, highlightAnchor, readJSON } from "./ui";
import { rid } from "./undo";

Alpine.data("archivePage", () => ({
  ...page(),
  board: readJSON("vm-page-data"),
  selected: [],
  highlighted: null,
  formatDate,

  init() {
    this.initPage();
    highlightAnchor(this);
  },
  get canEdit() {
    return this.board.role !== "observer";
  },
  get groups() {
    return [...this.board.lists]
      .sort(byPosition)
      .map((list) => ({ ...list, tasks: list.tasks.filter((t) => t.state === "archived") }))
      .filter((list) => list.tasks.length);
  },
  async reload() {
    try {
      this.board = await op("board_archive", { board_id: this.board.id });
      this.selected = [];
    } catch (error) {
      failToast(error);
    }
  },
  unarchive() {
    const ids = [...this.selected];
    if (!ids.length) return;
    this.perform(
      () => {
        this.board.lists.forEach((l) => l.tasks.forEach((t) => ids.includes(t.id) && (t.state = "done")));
        this.selected = [];
      },
      () => op("tasks_transition", { task_ids: ids, state: "done" }),
      () => {
        const current = () => ids.map((id) => rid("task", id));
        return ["unarchive selected", () => op("tasks_transition", { task_ids: current(), state: "archived" }),
          () => op("tasks_transition", { task_ids: current(), state: "done" })];
      },
    );
  },
}));
