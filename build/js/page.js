import Sortable from "sortablejs";
import { queue } from "./api";
import { failToast } from "./ui";
import { record, setFailureHandler } from "./undo";

const POLL_MS = 60_000;
const CHECK_MS = 1_000;

const timers = new Set();
let dragging = false;
let changes = 0;

// setTimeout that holds back polling until it has fired.
export function later(fn, ms) {
  const id = setTimeout(() => {
    timers.delete(id);
    fn();
  }, ms);
  timers.add(id);
  return id;
}

export function cancel(id) {
  clearTimeout(id);
  timers.delete(id);
}

function editing() {
  const field = document.activeElement?.closest("input:not([type=checkbox]), textarea, select, [contenteditable]");
  const overlay = [...document.querySelectorAll(".vm-overlay")].some((el) => el.checkVisibility());
  return Boolean(field) || overlay;
}

/**
 * Shared behaviour of pages that change data: optimistic apply, serial sending, undo entries, reload on failure, polling.
 * The page provides fetchData() and applyData(data).
 */
export function page() {
  return {
    run: queue(),
    initPage() {
      setFailureHandler(() => this.reload());
      let polledAt = Date.now();
      const poll = () => {
        if (document.hidden || Date.now() - polledAt < POLL_MS || !this.idle()) return;
        polledAt = Date.now();
        this.refresh();
      };
      document.addEventListener("visibilitychange", () => {
        polledAt = 0;
        poll();
      });
      setInterval(poll, CHECK_MS);
    },
    idle() {
      return !this.run.busy() && !dragging && !timers.size && !editing();
    },
    async reload() {
      try {
        this.applyData(await this.fetchData());
      } catch (error) {
        failToast(error);
      }
    },
    // Background reload: errors stay silent and data is dropped when the user acted meanwhile.
    async refresh() {
      const before = changes;
      try {
        const data = await this.fetchData();
        if (changes === before && this.idle()) this.applyData(data);
      } catch {}
    },
    // entry(result) returns [label, undo, redo]; both are async functions of operation calls.
    async perform(apply, send, entry) {
      changes++;
      if (apply) apply();
      try {
        const result = await this.run(send);
        if (entry) {
          const [label, undo, redo] = entry(result);
          record(label, () => this.replay(undo), () => this.replay(redo));
        }
        return result;
      } catch (error) {
        failToast(error);
        await this.reload();
        return undefined;
      }
    },
    async replay(step) {
      changes++;
      await this.run(step);
      await this.reload();
    },
  };
}

export const byPosition = (a, b) => a.position - b.position;

// Rendered cards keep tracking the objects they were created for, so reloads update those objects in place.
export function mergeById(current, incoming, merge = Object.assign) {
  return incoming.map((item) => {
    const existing = current.find((c) => String(c.id) === String(item.id));
    if (!existing) return item;
    merge(existing, item);
    return existing;
  });
}

let tempId = 0;
export const newTempId = (prefix) => `${prefix}${++tempId}`;

let lastDragEnd = 0;

// The click that ends a drag is no tap: it must not toggle, delete, rename, open or follow a link.
document.addEventListener("click", (event) => {
  if (Date.now() - lastDragEnd < 300) {
    event.preventDefault();
    event.stopPropagation();
  }
}, true);

// Matches the vm-flash animation length.
const FLASH_MS = 500;

// Alpine may re-render the dropped item as a new node, so it is found again by its data-*-id.
function flashDropped(item, draggable) {
  const attr = item.getAttributeNames().find((name) => /^data-.+-id$/.test(name));
  if (!attr) return;
  later(() => {
    const el = document.querySelector(`${draggable}[${attr}="${item.getAttribute(attr)}"]`);
    if (!el) return;
    el.classList.remove("vm-flash");
    void el.offsetWidth;
    el.classList.add("vm-flash");
    later(() => el.classList.remove("vm-flash"), FLASH_MS);
  });
}

/**
 * SortableJS in pointer fallback mode (same on mouse and touch), with Alpine keeping the DOM.
 * onDrop(event) runs when the item landed elsewhere; onOutside(event) when it was released outside every dropZone element.
 */
export function makeSortable(el, { onDrop, onOutside, dropZone, ...options }) {
  let first = null;
  let last = null;
  const track = (event) => {
    const point = event.touches ? event.touches[0] : event;
    last = { x: point.clientX, y: point.clientY };
    first = first || last;
  };
  return Sortable.create(el, {
    animation: 120,
    forceFallback: true,
    fallbackTolerance: 4,
    delay: 200,
    delayOnTouchOnly: true,
    filter: "input:not([type=checkbox]), textarea, select",
    preventOnFilter: false,
    onStart(event) {
      dragging = true;
      changes++;
      event.item._vmNext = event.item.nextSibling;
      first = last = null;
      document.addEventListener("pointermove", track);
      document.addEventListener("touchmove", track);
    },
    onEnd(event) {
      dragging = false;
      document.removeEventListener("pointermove", track);
      document.removeEventListener("touchmove", track);
      // Alpine owns the DOM: put the element back and let the state change re-render it.
      event.from.insertBefore(event.item, event.item._vmNext);
      const moved = first && Math.hypot(last.x - first.x, last.y - first.y) > 4;
      if (moved) lastDragEnd = Date.now();
      const released = moved && document.elementFromPoint(last.x, last.y);
      if (onOutside && moved && !(released && released.closest(dropZone))) onOutside(event);
      else if (event.from !== event.to || event.oldDraggableIndex !== event.newDraggableIndex) onDrop(event);
      else return;
      flashDropped(event.item, options.draggable);
    },
    ...options,
  });
}
