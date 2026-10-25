import { queue } from "./api";
import { failToast } from "./ui";
import { record, setFailureHandler } from "./undo";

// Shared behaviour of pages that change data: optimistic apply, serial sending, undo entries, reload on failure.
export function page() {
  return {
    run: queue(),
    initPage() {
      setFailureHandler(() => this.reload());
    },
    // entry(result) returns [label, undo, redo]; both are async functions of operation calls.
    async perform(apply, send, entry) {
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
      await this.run(step);
      await this.reload();
    },
  };
}

export const byPosition = (a, b) => a.position - b.position;

let tempId = 0;
export const newTempId = (prefix) => `${prefix}${++tempId}`;
