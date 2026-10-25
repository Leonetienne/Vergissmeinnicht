import Alpine from "alpinejs";
import { op } from "./api";
import { byPosition, makeSortable, mergeById, newTempId, page } from "./page";
import { dueClass, failToast, formatDate, highlightAnchor, readJSON } from "./ui";
import { remap, rid } from "./undo";

const COLOURS = ["none", "red", "orange", "yellow", "green", "blue", "purple", "grey", "turquoise"];
const STATE_ORDER = { open: 0, done: 1, archived: 2 };

function withoutArchived(board) {
  board.lists.forEach((list) => (list.tasks = list.tasks.filter((t) => t.state !== "archived")));
  return board;
}

function taskArgs(task) {
  const { title, position, state, due_date, colour, note } = task;
  return { list_id: rid("list", task.list_id), title, position, state, due_date, colour, note };
}

function bySortOrder(a, b) {
  return STATE_ORDER[a.state] - STATE_ORDER[b.state] || a.position - b.position;
}

// The board page and its archive share this component; the archive shows archived tasks with selection instead of editing.
Alpine.data("boardPage", (archive = false) => ({
  ...page(),
  archive,
  board: archive ? readJSON("vm-page-data") : withoutArchived(readJSON("vm-page-data")),
  highlighted: null,
  creatingList: false,
  newListTitle: "",
  single: null,
  noteDraft: "",
  selected: [],
  share: { open: false, rows: [], removed: [], query: "", candidates: [], active: 0, saving: false },
  colours: COLOURS,
  formatDate,
  dueClass,

  init() {
    this.initPage();
    highlightAnchor(this);
    window.addEventListener("hashchange", () => highlightAnchor(this));
    this.$nextTick(() => this.initListSort());
  },

  get canEdit() {
    return this.board.role !== "observer";
  },
  get editable() {
    return this.canEdit && !this.archive;
  },
  get isOwner() {
    return this.board.role === "owner";
  },
  get sortedLists() {
    return [...this.board.lists].sort(byPosition);
  },
  get hasCustomLists() {
    return this.board.lists.some((l) => !l.is_default);
  },
  // The empty default list hides once other lists exist; a task dropped outside every list brings it back.
  get shownLists() {
    return this.sortedLists.filter((l) => !l.is_default || !this.hasCustomLists || this.visibleTasks(l).length);
  },
  get anyVisible() {
    return this.board.lists.some((l) => this.visibleTasks(l).length);
  },
  visibleTasks(list) {
    const states = this.archive ? ["archived"] : ["open", "done"];
    return list.tasks.filter((t) => states.includes(t.state)).sort(bySortOrder);
  },
  listById(id) {
    return this.board.lists.find((l) => String(l.id) === String(id));
  },
  findTask(id) {
    for (const list of this.board.lists) {
      const task = list.tasks.find((t) => String(t.id) === String(id));
      if (task) return task;
    }
    return null;
  },
  get defaultList() {
    return this.board.lists.find((l) => l.is_default);
  },

  async reload() {
    try {
      const data = this.archive
        ? await op("board_archive", { board_id: this.board.id })
        : withoutArchived(await op("board_get", { board_id: this.board.id }));
      const { lists, ...fields } = data;
      Object.assign(this.board, fields);
      this.board.lists = mergeById(this.board.lists, lists, (list, fresh) => {
        const { tasks, ...rest } = fresh;
        Object.assign(list, rest);
        list.tasks = mergeById(list.tasks, tasks);
      });
      this.selected = this.selected.filter((id) => this.findTask(id));
      if (this.single) {
        this.single = this.findTask(this.single.id);
        if (this.single) this.noteDraft = this.single.note;
      }
    } catch (error) {
      failToast(error);
    }
  },

  // Board
  updateBoard(fields) {
    const old = Object.fromEntries(Object.keys(fields).map((k) => [k, this.board[k]]));
    const label = "title" in fields ? "rename board" : "change emoji";
    const follow = (result) => {
      if (!result) return;
      this.board.url = result.url;
      history.replaceState(null, "", result.url + location.hash);
    };
    this.perform(
      () => Object.assign(this.board, fields),
      async () => follow(await op("board_update", { board_id: this.board.id, ...fields })),
      () => [label, async () => follow(await op("board_update", { board_id: this.board.id, ...old })),
        async () => follow(await op("board_update", { board_id: this.board.id, ...fields }))],
    );
  },
  async deleteBoard() {
    if (!(await window.confirmDialog(`Delete board ${this.board.title} with all its lists and tasks?`))) return;
    try {
      await this.run(() => op("board_delete", { board_id: this.board.id }));
      location.href = "/";
    } catch (error) {
      failToast(error);
    }
  },
  async leaveBoard() {
    if (!(await window.confirmDialog(`Leave board ${this.board.title}? Your access ends.`))) return;
    try {
      await this.run(() => op("board_leave", { board_id: this.board.id }));
      location.href = "/";
    } catch (error) {
      failToast(error);
    }
  },
  archiveDone() {
    const done = this.board.lists.flatMap((l) => l.tasks.filter((t) => t.state === "done"));
    this.perform(
      () => done.forEach((t) => (t.state = "archived")),
      () => op("board_archive_done", { board_id: this.board.id }),
      (result) => {
        const ids = () => result.task_ids.map((id) => rid("task", id));
        return ["archive what's done", () => op("tasks_transition", { task_ids: ids(), state: "done" }),
          () => op("tasks_transition", { task_ids: ids(), state: "archived" })];
      },
    );
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

  // Lists
  startCreateList() {
    this.creatingList = true;
    this.newListTitle = "";
    setTimeout(() => this.$refs.newList.focus());
  },
  listTitleTaken(title, except) {
    const wanted = title.toLowerCase();
    const taken = this.board.lists.some((l) => l !== except && l.title.toLowerCase() === wanted);
    if (taken) window.toast(`List ${title} already exists on this board`);
    return taken;
  },
  createList() {
    const title = this.newListTitle.trim();
    if (title && this.listTitleTaken(title)) return;
    this.creatingList = false;
    if (!title) return;
    let list = { id: newTempId("list"), board_id: this.board.id, title, is_default: false,
      position: this.board.lists.length, tasks: [] };
    this.perform(
      () => {
        this.board.lists.push(list);
        list = this.board.lists[this.board.lists.length - 1];
      },
      () => op("list_create", { board_id: this.board.id, title }),
      (created) => {
        Object.assign(list, { id: created.id, position: created.position });
        return ["create list", () => op("list_delete", { list_id: rid("list", created.id) }), async () => {
          const previous = rid("list", created.id);
          const again = await op("list_create", { board_id: this.board.id, title, position: created.position });
          remap("list", previous, again.id);
        }];
      },
    );
  },
  renameList(list, title) {
    if (this.listTitleTaken(title, list)) return;
    const old = list.title;
    this.perform(
      () => (list.title = title),
      () => op("list_update", { list_id: list.id, title }),
      () => ["rename list", () => op("list_update", { list_id: rid("list", list.id), title: old }),
        () => op("list_update", { list_id: rid("list", list.id), title })],
    );
  },
  async deleteList(list) {
    if (!(await window.confirmDialog("Delete this list? Its tasks move to the default list."))) return;
    const target = this.defaultList;
    const snapshot = { id: list.id, title: list.title, position: list.position };
    this.perform(
      () => {
        let next = Math.max(-1, ...target.tasks.map((t) => t.position)) + 1;
        list.tasks.sort(byPosition).forEach((t) => {
          t.list_id = target.id;
          t.position = next++;
          target.tasks.push(t);
        });
        this.board.lists = this.board.lists.filter((l) => l !== list);
        this.board.lists.filter((l) => l.position > list.position).forEach((l) => l.position--);
      },
      () => op("list_delete", { list_id: list.id }),
      (result) => {
        result.moved.forEach((moved) => {
          const task = this.findTask(moved.id);
          if (task) task.position = moved.position;
        });
        return ["delete list", async () => {
          const previous = rid("list", snapshot.id);
          const restored = await op("list_create", { board_id: this.board.id, title: snapshot.title, position: snapshot.position });
          remap("list", previous, restored.id);
          // Moved tasks were gapless 0..n-1 in the deleted list, so index equals former position.
          const moves = result.moved.map((t, index) => ({ task_id: rid("task", t.id), list_id: restored.id, position: index }));
          if (moves.length) await op("tasks_move", { moves });
        }, () => op("list_delete", { list_id: rid("list", snapshot.id) })];
      },
    );
  },
  initListSort() {
    if (!this.editable) return;
    makeSortable(this.$refs.board, {
      draggable: ".vm-list--custom",
      handle: ".vm-list__header",
      onDrop: (e) => this.moveList(this.listById(e.item.dataset.listId), e.newDraggableIndex + 1),
    });
  },
  moveList(list, position) {
    const old = list.position;
    this.perform(
      () => {
        const custom = this.sortedLists.filter((l) => !l.is_default && l !== list);
        custom.splice(position - 1, 0, list);
        custom.forEach((l, index) => (l.position = index + 1));
      },
      () => op("list_move", { list_id: list.id, position }),
      () => ["move list", () => op("list_move", { list_id: rid("list", list.id), position: old }),
        () => op("list_move", { list_id: rid("list", list.id), position })],
    );
  },

  // Tasks
  createTask(list, input) {
    const title = input.value.trim();
    if (!title) return;
    input.value = "";
    let task = { id: newTempId("task"), list_id: list.id, title, state: "open",
      position: Math.max(-1, ...list.tasks.map((t) => t.position)) + 1, due_date: null, colour: "none", note: "" };
    this.perform(
      () => {
        list.tasks.push(task);
        task = list.tasks[list.tasks.length - 1];
      },
      () => op("task_create", { list_id: list.id, title }),
      (created) => {
        Object.assign(task, created);
        return ["create task", () => op("task_delete", { task_id: rid("task", created.id) }), async () => {
          const previous = rid("task", created.id);
          const again = await op("task_create", taskArgs(created));
          remap("task", previous, again.id);
        }];
      },
    );
  },
  updateTask(task, fields) {
    const old = Object.fromEntries(Object.keys(fields).map((k) => [k, task[k]]));
    this.perform(
      () => Object.assign(task, fields),
      () => op("task_update", { task_id: task.id, ...fields }),
      () => ["edit task", () => op("task_update", { task_id: rid("task", task.id), ...old }),
        () => op("task_update", { task_id: rid("task", task.id), ...fields })],
    );
  },
  toggle(task, checkbox) {
    if (!this.editable) return;
    const from = task.state;
    const to = from === "open" ? "done" : "open";
    checkbox.checked = to === "done";
    this.perform(
      () => (task.state = to),
      () => op("task_transition", { task_id: task.id, state: to }),
      () => [to === "done" ? "check task" : "uncheck task",
        () => op("task_transition", { task_id: rid("task", task.id), state: from }),
        () => op("task_transition", { task_id: rid("task", task.id), state: to })],
    );
  },
  async deleteTask(task) {
    if (!(await window.confirmDialog(`Delete task ${task.title}?`))) return;
    const list = this.listById(task.list_id);
    this.perform(
      () => {
        list.tasks = list.tasks.filter((t) => t !== task);
        list.tasks.forEach((t) => t.position > task.position && t.position--);
        if (this.single === task) this.single = null;
      },
      () => op("task_delete", { task_id: task.id }),
      () => {
        const snapshot = { ...task };
        return ["delete task", async () => {
          const previous = rid("task", snapshot.id);
          const restored = await op("task_create", taskArgs(snapshot));
          remap("task", previous, restored.id);
        }, () => op("task_delete", { task_id: rid("task", snapshot.id) })];
      },
    );
  },
  initTaskSort(el) {
    if (!this.editable) return;
    makeSortable(el, {
      group: "tasks",
      draggable: ".vm-card",
      emptyInsertThreshold: 24,
      onDrop: (e) => {
        const task = this.findTask(e.item.dataset.taskId);
        const list = this.listById(e.to.dataset.listId);
        if (task && list) this.moveTask(task, list, e.newDraggableIndex);
      },
      dropZone: ".vm-list",
      onOutside: (e) => {
        const task = this.findTask(e.item.dataset.taskId);
        if (task && String(task.list_id) !== String(this.defaultList.id)) {
          this.moveTask(task, this.defaultList, this.visibleTasks(this.defaultList).length);
        }
      },
    });
  },
  // index is the drop position among the list's visible cards; tasks keep their state and land among their own state.
  moveTask(task, toList, index) {
    const fromList = this.listById(task.list_id);
    const cards = this.visibleTasks(toList).filter((t) => t !== task);
    cards.splice(index, 0, task);
    const group = cards.filter((t) => t.state === task.state);
    const at = group.indexOf(task);
    let position;
    if (group[at + 1]) position = group[at + 1].position;
    else if (group[at - 1]) position = group[at - 1].position + 1;
    else position = Math.max(-1, ...toList.tasks.filter((t) => t !== task).map((t) => t.position)) + 1;
    if (fromList === toList && task.position < position) position -= 1;
    if (fromList === toList && task.position === position) return;
    const old = { list: fromList, position: task.position };
    this.perform(
      () => {
        fromList.tasks = fromList.tasks.filter((t) => t !== task);
        fromList.tasks.forEach((t) => t.position > task.position && t.position--);
        toList.tasks.forEach((t) => t.position >= position && t.position++);
        Object.assign(task, { position, list_id: toList.id });
        toList.tasks.push(task);
      },
      () => op("task_move", { task_id: task.id, list_id: toList.id, position }),
      () => ["move task",
        () => op("task_move", { task_id: rid("task", task.id), list_id: rid("list", old.list.id), position: old.position }),
        () => op("task_move", { task_id: rid("task", task.id), list_id: rid("list", toList.id), position })],
    );
  },

  // Singleview
  openSingle(task) {
    this.single = task;
    this.noteDraft = task.note;
  },
  closeSingle() {
    if (document.activeElement) document.activeElement.blur();
    this.saveNote();
    this.single = null;
  },
  saveField(field, value) {
    if (!this.editable || !this.single || this.single[field] === value) return;
    this.updateTask(this.single, { [field]: value });
  },
  saveNote() {
    if (!this.editable || !this.single) return;
    const note = this.noteDraft.trim();
    if (note !== this.single.note) this.updateTask(this.single, { note });
  },

  // Sharing: changes collect in the dialog and apply on Save.
  async openShare() {
    this.share = { open: true, rows: [], removed: [], query: "", candidates: [], active: 0, saving: false };
    setTimeout(() => this.$refs.shareSearch.focus());
    try {
      const shares = await op("shares_list", { board_id: this.board.id });
      this.share.rows = shares.map((s) => ({ id: s.id, user: s.user, role: s.role, saved: s.role }));
    } catch (error) {
      failToast(error);
    }
  },
  async searchCandidates() {
    const q = this.share.query.trim();
    if (q.length < 3) {
      this.share.candidates = [];
      return;
    }
    try {
      const found = await op("share_candidates", { board_id: this.board.id, q });
      if (q !== this.share.query.trim()) return;
      const chosen = new Set(this.share.rows.map((r) => r.user.id));
      this.share.candidates = found.filter((u) => !chosen.has(u.id));
      this.share.active = 0;
    } catch (error) {
      failToast(error);
    }
  },
  moveCandidate(step) {
    const count = this.share.candidates.length;
    if (count) this.share.active = (this.share.active + step + count) % count;
  },
  pickCandidate(user) {
    if (!user) return;
    const removed = this.share.removed.find((r) => r.user.id === user.id);
    this.share.removed = this.share.removed.filter((r) => r !== removed);
    this.share.rows.push(removed || { id: null, user, role: "observer", saved: null });
    this.share.query = "";
    this.share.candidates = [];
    this.$refs.shareSearch.focus();
  },
  dropRow(row) {
    this.share.rows = this.share.rows.filter((r) => r !== row);
    if (row.id) this.share.removed.push(row);
  },
  get shareDirty() {
    return this.share.removed.length > 0 || this.share.rows.some((r) => r.role !== r.saved);
  },
  async saveShares() {
    this.share.saving = true;
    try {
      for (const row of this.share.removed) await op("share_remove", { share_id: row.id });
      for (const row of this.share.rows) {
        if (!row.id) await op("share_add", { board_id: this.board.id, user_id: row.user.id, role: row.role });
        else if (row.role !== row.saved) await op("share_update", { share_id: row.id, role: row.role });
      }
      this.share.open = false;
      window.toast("Sharing saved");
    } catch (error) {
      failToast(error);
      await this.openShare();
    } finally {
      this.share.saving = false;
    }
  },
}));
