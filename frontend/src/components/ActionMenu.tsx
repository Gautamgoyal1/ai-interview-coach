import { useEffect, useId, useRef, useState } from "react";
import { Link } from "react-router-dom";
import "./OverlayControls.css";

export interface ActionMenuItem {
  label: string;
  to?: string;
  onClick?: () => void;
  tone?: "default" | "danger";
}

interface ActionMenuProps {
  label: string;
  items: ActionMenuItem[];
}

export default function ActionMenu({ label, items }: ActionMenuProps) {
  const [open, setOpen] = useState(false);
  const menuId = useId();
  const wrapRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;

    function handleOutside(event: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    window.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleOutside);
      window.removeEventListener("keydown", handleKey);
    };
  }, [open]);

  return (
    <div className="pm-menu-wrap" ref={wrapRef}>
      <button
        type="button"
        className="pm-menu-trigger"
        aria-label={label}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        onClick={() => setOpen((prev) => !prev)}
      >
        <span aria-hidden="true">⋯</span>
      </button>

      {open && (
        <div id={menuId} className="pm-menu-dropdown" role="menu">
          {items.map((item) =>
            item.to ? (
              <Link
                key={item.label}
                to={item.to}
                role="menuitem"
                className={`pm-menu-item${item.tone === "danger" ? " danger" : ""}`}
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ) : (
              <button
                key={item.label}
                type="button"
                role="menuitem"
                className={`pm-menu-item${item.tone === "danger" ? " danger" : ""}`}
                onClick={() => {
                  setOpen(false);
                  item.onClick?.();
                }}
              >
                {item.label}
              </button>
            ),
          )}
        </div>
      )}
    </div>
  );
}
