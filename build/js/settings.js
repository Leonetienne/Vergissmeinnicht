import Alpine from "alpinejs";
import { readJSON } from "./ui";

const CSS_FORBIDDEN = /[<>{}&@`\\]/g;

Alpine.data("settingsPage", () => {
  const appearance = readJSON("vm-appearance") || {};
  return {
    css: appearance.css || "",
    cssMobile: appearance.cssMobile || "",
    uiOpacity: appearance.uiOpacity ?? 100,
    backdropOpacity: appearance.backdropOpacity ?? 100,

    init() {
      this.$watch("backdropOpacity", () => this.preview());
    },
    preview() {
      const css = this.css.replace(CSS_FORBIDDEN, "");
      const mobile = this.cssMobile.replace(CSS_FORBIDDEN, "");
      const style = document.getElementById("vm-backdrop-css");
      if (style) style.textContent = `.vm-backdrop { ${css} } @media (max-width: 768px) { .vm-backdrop { ${mobile} } }`;
      document.documentElement.style.setProperty("--ui-alpha", `${this.uiOpacity}%`);
      const backdrop = document.querySelector(".vm-backdrop");
      if (backdrop) backdrop.style.opacity = this.backdropOpacity / 100;
    },
    async copy(text) {
      try {
        await navigator.clipboard.writeText(text.trim());
        window.toast("Copied");
      } catch {
        window.toast("Copy failed", { error: true });
      }
    },
    async confirmSubmit(form, message) {
      if (await window.confirmDialog(message)) form.submit();
    },
  };
});
