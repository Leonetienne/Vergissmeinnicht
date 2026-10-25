import Alpine from "alpinejs";

let toastId = 0;

Alpine.store("toasts", {
  items: [],
  show(message, error = false) {
    const id = ++toastId;
    this.items.push({ id, message, error });
    setTimeout(() => this.close(id), 5000);
  },
  close(id) {
    this.items = this.items.filter((t) => t.id !== id);
  },
});

Alpine.store("confirm", {
  open: false,
  message: "",
  ok: "OK",
  resolve: null,
  ask(message, ok = "OK") {
    if (this.resolve) this.resolve(false);
    this.message = message;
    this.ok = ok;
    this.open = true;
    return new Promise((resolve) => {
      this.resolve = resolve;
    });
  },
  answer(value) {
    this.open = false;
    const resolve = this.resolve;
    this.resolve = null;
    if (resolve) resolve(value);
  },
});

window.toast = (message, { error = false } = {}) => Alpine.store("toasts").show(message, error);
window.confirmDialog = (message, ok) => Alpine.store("confirm").ask(message, ok);

export function readJSON(id) {
  const el = document.getElementById(id);
  return el ? JSON.parse(el.textContent) : null;
}

export function showServerMessages() {
  document.querySelectorAll("[data-toast]").forEach((el) => {
    window.toast(el.dataset.toast, { error: el.dataset.error === "1" });
    el.remove();
  });
}

function parseDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function formatDate(iso) {
  if (!iso) return "";
  const date = parseDate(iso);
  const options = { month: "short", day: "numeric" };
  if (date.getFullYear() !== new Date().getFullYear()) options.year = "numeric";
  return date.toLocaleDateString("en-US", options);
}

export function dueClass(task) {
  if (task.state !== "open" || !task.due_date) return "";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Math.round((parseDate(task.due_date) - today) / 86400000);
  if (days <= 0) return "vm-due--now";
  if (days <= 3) return "vm-due--soon";
  return "";
}

// Scrolls to #task-<id> and returns the id for a brief highlight.
export function anchoredTask() {
  const match = location.hash.match(/^#task-(\d+)$/);
  return match ? Number(match[1]) : null;
}

export function highlightAnchor(component) {
  const id = anchoredTask();
  if (!id) return;
  component.highlighted = id;
  component.$nextTick(() => {
    const el = document.getElementById("task-" + id);
    if (el) el.scrollIntoView({ block: "center" });
    setTimeout(() => (component.highlighted = null), 2000);
  });
}

export function failToast(error) {
  window.toast(error.message || String(error), { error: true });
}
