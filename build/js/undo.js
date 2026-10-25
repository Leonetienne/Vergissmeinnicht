// Per-page undo and redo. Each entry holds async undo/redo functions built from ordinary operation calls.
import { failToast } from "./ui";

const LIMIT = 100;
const undoStack = [];
const redoStack = [];
const ids = new Map();
let busy = false;
let onFailure = null;

// Resolves an id through recreations so older entries reach the item that replaced it.
export function rid(kind, id) {
  let key = `${kind}:${id}`;
  while (ids.has(key)) {
    id = ids.get(key);
    key = `${kind}:${id}`;
  }
  return id;
}

export function remap(kind, oldId, newId) {
  if (oldId !== newId) ids.set(`${kind}:${oldId}`, newId);
}

export function record(label, undo, redo) {
  undoStack.push({ label, undo, redo });
  if (undoStack.length > LIMIT) undoStack.shift();
  redoStack.length = 0;
}

export function setFailureHandler(handler) {
  onFailure = handler;
}

async function run(from, to, direction) {
  if (busy || !from.length) return;
  busy = true;
  const entry = from.pop();
  try {
    await entry[direction]();
    to.push(entry);
    window.toast(`${direction === "undo" ? "Undo" : "Redo"}: ${entry.label}`);
  } catch (error) {
    failToast(error);
    if (onFailure) await onFailure();
  } finally {
    busy = false;
  }
}

const NON_TEXT_INPUTS = ["checkbox", "radio", "button", "submit", "range", "file", "color"];

function inTextField(target) {
  const field = target.closest("input, textarea, [contenteditable]");
  return field && !(field.tagName === "INPUT" && NON_TEXT_INPUTS.includes(field.type));
}

document.addEventListener("keydown", (event) => {
  if (!(event.ctrlKey || event.metaKey) || event.altKey || inTextField(event.target)) return;
  const key = event.key.toLowerCase();
  if (key === "z" && !event.shiftKey) {
    event.preventDefault();
    run(undoStack, redoStack, "undo");
  } else if ((key === "z" && event.shiftKey) || key === "y") {
    event.preventDefault();
    run(redoStack, undoStack, "redo");
  }
});
