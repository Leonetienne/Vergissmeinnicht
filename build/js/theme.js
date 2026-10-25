import Alpine from "alpinejs";
import { op } from "./api";
import { failToast } from "./ui";

const root = document.documentElement;
const ATTRIBUTE = { theme: "theme", color_mode: "mode" };

Alpine.data("themeMenu", () => ({
  open: false,
  theme: root.dataset.theme,
  mode: root.dataset.mode,

  async set(field, value) {
    const key = ATTRIBUTE[field];
    const previous = root.dataset[key];
    if (previous === value) return;
    this.apply(key, value);
    try {
      await op("profile_update", { [field]: value });
    } catch (error) {
      this.apply(key, previous);
      failToast(error);
    }
  },
  apply(key, value) {
    root.dataset[key] = value;
    this[key] = value;
  },
}));
