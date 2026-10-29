import Alpine from "alpinejs";
import { op } from "./api";
import { makeSortable, mergeById, newTempId, page } from "./page";
import { readJSON } from "./ui";
import { remap, rid } from "./undo";

Alpine.data("boardList", () => {
  const data = readJSON("vm-page-data");
  return {
    ...page(),
    own: data.own,
    shared: data.shared,

    init() {
      this.initPage();
      makeSortable(this.$refs.own, {
        draggable: ".vm-board-entry",
        onDrop: (e) => {
          const board = this.own.find((b) => String(b.id) === e.item.dataset.boardId);
          if (board) this.move(board, e.oldDraggableIndex, e.newDraggableIndex);
        },
      });
    },
    fetchData() {
      return op("boards_list");
    },
    applyData(fresh) {
      this.own = mergeById(this.own, fresh.own);
      this.shared = mergeById(this.shared, fresh.shared);
    },

    titleTaken(title, except) {
      const wanted = title.toLowerCase();
      const taken = this.own.some((b) => b !== except && b.title.toLowerCase() === wanted);
      if (taken) window.toast(`Board ${title} already exists`);
      return taken;
    },
    create(input) {
      const title = input.value.trim();
      if (!title || this.titleTaken(title)) return;
      input.value = "";
      let board = { id: newTempId("board"), title, emoji: "", description: "", url: "#", role: "owner" };
      this.perform(
        () => {
          this.own.push(board);
          board = this.own[this.own.length - 1];
        },
        () => op("board_create", { title }),
        (created) => {
          Object.assign(board, created);
          return ["create board", () => op("board_delete", { board_id: rid("board", created.id) }), async () => {
            const previous = rid("board", created.id);
            const again = await op("board_create", { title, position: this.own.indexOf(board) });
            remap("board", previous, again.id);
          }];
        },
      );
    },
    update(board, fields, label) {
      const old = Object.fromEntries(Object.keys(fields).map((k) => [k, board[k]]));
      this.perform(
        () => Object.assign(board, fields),
        async () => Object.assign(board, await op("board_update", { board_id: board.id, ...fields })),
        () => [label, () => op("board_update", { board_id: rid("board", board.id), ...old }),
          () => op("board_update", { board_id: rid("board", board.id), ...fields })],
      );
    },
    rename(board, title) {
      if (this.titleTaken(title, board)) return;
      this.update(board, { title }, "rename board");
    },
    setEmoji(board, emoji) {
      this.update(board, { emoji }, "change emoji");
    },
    move(board, from, to) {
      this.perform(
        () => {
          this.own.splice(from, 1);
          this.own.splice(to, 0, board);
        },
        () => op("board_move", { board_id: board.id, position: to }),
        () => ["move board", () => op("board_move", { board_id: rid("board", board.id), position: from }),
          () => op("board_move", { board_id: rid("board", board.id), position: to })],
      );
    },
  };
});
