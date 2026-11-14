import { useEffect, useRef, type RefObject } from "react";

/** Contain keyboard focus and make sibling branches inactive while a modal is open. */
export function useModalFocus(open: boolean, root: RefObject<HTMLElement>, onEscape: () => void) {
  const escape = useRef(onEscape);
  escape.current = onEscape;
  useEffect(() => {
    const panel = root.current;
    if (!open || !panel) return;
    const previous = document.activeElement as HTMLElement | null;
    const panelWasInert = panel.inert;
    panel.inert = false;
    const inactive: Array<[HTMLElement, boolean]> = [];
    let branch: HTMLElement = panel;
    while (branch.parentElement && branch !== document.body) {
      for (const sibling of Array.from(branch.parentElement.children)) {
        if (sibling !== branch && sibling instanceof HTMLElement && !sibling.hasAttribute("data-modal-backdrop")) {
          inactive.push([sibling, sibling.inert]);
          sibling.inert = true;
        }
      }
      branch = branch.parentElement;
    }
    const targets = () => Array.from(panel.querySelectorAll<HTMLElement>(
      'a[href],button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex="0"]',
    )).filter(element => element.getClientRects().length > 0);
    const focusFirst = () => (targets()[0] || panel).focus();
    (panel.querySelector<HTMLElement>("[data-modal-initial-focus]") || targets()[0] || panel).focus();
    function keydown(event: KeyboardEvent) {
      if (event.key === "Escape") { event.preventDefault(); escape.current(); }
      if (event.key !== "Tab") return;
      const elements = targets();
      const first = elements[0], last = elements[elements.length - 1];
      if (!first) { event.preventDefault(); panel!.focus(); return; }
      if (event.shiftKey && (document.activeElement === first || !panel!.contains(document.activeElement))) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !panel!.contains(document.activeElement))) {
        event.preventDefault(); first.focus();
      }
    }
    function contain(event: FocusEvent) { if (!panel!.contains(event.target as Node)) focusFirst(); }
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", keydown);
    document.addEventListener("focusin", contain);
    return () => {
      document.removeEventListener("keydown", keydown);
      document.removeEventListener("focusin", contain);
      inactive.forEach(([element, inert]) => { element.inert = inert; });
      panel.inert = panelWasInert;
      document.body.style.overflow = overflow;
      if (previous?.isConnected) previous.focus();
    };
  }, [open, root]);
}
