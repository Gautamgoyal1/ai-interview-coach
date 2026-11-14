import { useContext, useEffect, useRef } from "react";
import { UNSAFE_NavigationContext } from "react-router-dom";

export const UNSENT_ANSWER_WARNING =
  "You have an unsent answer. Leaving will discard it. Drafts are not saved. Leave anyway?";
export function confirmDiscardAnswer(dirty: boolean): boolean {
  return !dirty || window.confirm(UNSENT_ANSWER_WARNING);
}

// BrowserRouter installs a window popstate listener while rendering. Register this
// dispatcher at module initialization so a cancelled transition is intercepted
// before the router can unmount the workspace and remove its guard.
let activePopGuard: ((event: PopStateEvent) => void) | undefined;
let listeningWindow: Window | undefined;
const dispatchPop = (event: PopStateEvent) => activePopGuard?.(event);
function ensurePopDispatcher() {
  if (typeof window === "undefined" || listeningWindow === window) return;
  listeningWindow?.removeEventListener("popstate", dispatchPop, true);
  listeningWindow = window;
  window.addEventListener("popstate", dispatchPop, true);
}
ensurePopDispatcher();

/** Guard router links, browser history and refresh without pretending drafts are durable. */
export function useUnsentAnswerWarning(dirty: boolean) {
  const { navigator } = useContext(UNSAFE_NavigationContext);
  const dirtyRef = useRef(dirty);
  dirtyRef.current = dirty;
  useEffect(() => {
    const originalPush = navigator.push;
    const originalReplace = navigator.replace;
    navigator.push = (...args) => {
      if (confirmDiscardAnswer(dirtyRef.current))
        originalPush.apply(navigator, args);
    };
    navigator.replace = (...args) => {
      if (confirmDiscardAnswer(dirtyRef.current))
        originalReplace.apply(navigator, args);
    };
    let index = window.history.state?.idx;
    let restoring = false;
    function onPop(event: PopStateEvent) {
      const nextIndex = event.state?.idx;
      if (restoring) {
        restoring = false;
        event.stopImmediatePropagation();
        return;
      }
      if (
        dirtyRef.current &&
        !confirmDiscardAnswer(true) &&
        typeof index === "number" &&
        typeof nextIndex === "number" &&
        index !== nextIndex
      ) {
        event.stopImmediatePropagation();
        restoring = true;
        window.history.go(index - nextIndex);
      } else {
        index = nextIndex;
      }
    }
    function onBeforeUnload(event: BeforeUnloadEvent) {
      if (!dirtyRef.current) return;
      event.preventDefault();
      event.returnValue = "";
    }
    ensurePopDispatcher();
    activePopGuard = onPop;
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => {
      navigator.push = originalPush;
      navigator.replace = originalReplace;
      if (activePopGuard === onPop) activePopGuard = undefined;
      window.removeEventListener("beforeunload", onBeforeUnload);
    };
  }, [navigator]);
}
