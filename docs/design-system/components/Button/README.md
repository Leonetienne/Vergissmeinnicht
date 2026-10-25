# Button

Buttons trigger one action; the label is a verb.

- `vm-btn` is the default (secondary) button: "Archive what's done", "Open archive", "Leave archive".
- `vm-btn--primary` for the single main action of a page or dialog ("Share", "Unarchive selected").
- `vm-btn--danger` only for confirming a destructive action and for "Delete account".
- `vm-btn--ghost vm-btn--sm` for low-key controls such as "Create list" above the lists.
- `vm-icon-btn` holds a 16px inline SVG or the glyphs "..." and "×"; give it an `aria-label`. Add `vm-icon-btn--danger` for delete.

Consumer provides: the label (or icon plus `aria-label`) and the click handler.

Do: one primary per view. Don't: hide controls behind hover only, cards are used on touch screens.
