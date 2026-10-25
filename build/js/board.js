import Alpine from "alpinejs";
import Sortable from "sortablejs";
import { op } from "./api";
import { byPosition, newTempId, page } from "./page";
import { dueClass, failToast, formatDate, highlightAnchor, readJSON } from "./ui";
import { remap, rid } from "./undo";

const COLOURS = ["none", "red", "orange", "yellow", "green", "blue", "purple", "grey", "turquoise"];

function withoutArchived(board) {
  board.lists.forEach((list) => (list.tasks = list.tasks.filter((t) => t.state !== "archived")));
  return board;
}

function taskArgs(task) {
  const { title, position, state, due_date, colour, note } = task;
  return { list_id: rid("list", task.list_id), title, position, state, due_date, colour, note };
}

function sortableOptions(onDrop, extra) {
  return {
    animation: 120,
    forceFallback: true,
    delay: 200,
    delayOnTouchOnly: true,
    filter: "button, input",
    preventOnFilter: false,
    onStart: (e) => (e.item._vmNext = e.item.nextSibling),
    onEnd: (e) => {
      // Alpine owns the DOM: put the element back and let the state change re-render it.
      e.from.insertBefore(e.item, e.item._vmNext);
      if (e.from === e.to && e.oldDraggableIndex === e.newDraggableIndex) return;
      onDrop(e);
    },
    ...extra,
  };
}

Alpine.data("boardPage", () => ({
  ...page(),
  board: withoutArchived(readJSON("vm-page-data")),
  highlighted: null,
  creatingList: false,
  newListTitle: "",
  single: null,
  noteDraft: "",
  share: { open: false, items: [], query: "", candidates: [] },
  colours: COLOURS,
  formatDate,
  dueClass,

  init() {
    this.initPage();
    highlightAnchor(this);
    this.$nextTick(() => this.initListSort());
  },

  get canEdit() {
    return this.board.role !== "observer";
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
  openTasks(list) {
    return list.tasks.filter((t) => t.state === "open").sort(byPosition);
  },
  doneTasks(list) {
    return list.tasks.filter((t) => t.state === "done").sort(byPosition);
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
      const data = withoutArchived(await op("board_get", { board_id: this.board.id }));
      this.board = data;
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
    const label = "name" in fields ? "rename board" : "change emoji";
    const apply = (result) => {
      if (!result) return;
      this.board.url = result.url;
      history.replaceState(null, "", result.url + location.hash);
    };
    this.perform(
      () => Object.assign(this.board, fields),
      async () => apply(await op("board_update", { board_id: this.board.id, ...fields })),
      () => [label, () => op("board_update", { board_id: this.board.id, ...old }),
        () => op("board_update", { board_id: this.board.id, ...fields })],
    );
  },
  async deleteBoard() {
    if (!(await window.confirmDialog(`Delete board ${this.board.name} with all its lists and tasks?`))) return;
    try {
      await this.run(() => op("board_delete", { board_id: this.board.id }));
      location.href = "/";
    } catch (error) {
      failToast(error);
    }
  },
  async leaveBoard() {
    if (!(await window.confirmDialog(`Leave board ${this.board.name}? Your access ends.`))) return;
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

  // Lists
  startCreateList() {
    this.creatingList = true;
    this.newListTitle = "";
    setTimeout(() => this.$refs.newList.focus());
  },
  createList() {
    const title = this.newListTitle.trim();
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
    if (!this.canEdit) return;
    Sortable.create(this.$refs.board, sortableOptions((e) => {
      const list = this.listById(e.item.dataset.listId);
      this.moveList(list, e.newDraggableIndex + 1);
    }, { draggable: ".vm-list--custom", handle: ".vm-list__header" }));
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
    if (!this.canEdit) return;
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
    if (!this.canEdit) return;
    Sortable.create(el, sortableOptions((e) => {
      const task = this.findTask(e.item.dataset.taskId);
      const list = this.listById(e.to.dataset.listId);
      if (task && list) this.moveTask(task, list, e.newDraggableIndex);
    }, { group: "tasks", draggable: ".vm-card", emptyInsertThreshold: 24 }));
  },
  moveTask(task, toList, index) {
    const fromList = this.listById(task.list_id);
    const others = this.openTasks(toList).filter((t) => t !== task);
    let position = 0;
    if (index < others.length) position = others[index].position;
    else if (others.length) position = others[others.length - 1].position + 1;
    if (fromList === toList && task.position < position) position -= 1;
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
    if (!this.canEdit || !this.single || this.single[field] === value) return;
    this.updateTask(this.single, { [field]: value });
  },
  saveNote() {
    if (!this.canEdit || !this.single) return;
    const note = this.noteDraft.trim();
    if (note !== this.single.note) this.updateTask(this.single, { note });
  },

  // Sharing
  async openShare() {
    this.share = { open: true, items: [], query: "", candidates: [] };
    setTimeout(() => this.$refs.shareSearch.focus());
    try {
      this.share.items = await op("shares_list", { board_id: this.board.id });
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
      this.share.candidates = await op("share_candidates", { board_id: this.board.id, q });
    } catch (error) {
      failToast(error);
    }
  },
  async addShare(user) {
    try {
      this.share.items.push(await op("share_add", { board_id: this.board.id, user_id: user.id }));
      this.share.query = "";
      this.share.candidates = [];
    } catch (error) {
      failToast(error);
    }
  },
  async setRole(share, role) {
    try {
      Object.assign(share, await op("share_update", { share_id: share.id, role }));
    } catch (error) {
      failToast(error);
    }
  },
  async removeShare(share) {
    try {
      await op("share_remove", { share_id: share.id });
      this.share.items = this.share.items.filter((s) => s !== share);
    } catch (error) {
      failToast(error);
    }
  },
}));
