import { useEffect, useId, useRef } from "react";
import "./OverlayControls.css";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  warningNote?: string;
  checkboxLabel?: string;
  checkboxChecked?: boolean;
  onCheckboxChange?: (checked: boolean) => void;
  confirmLabel?: string;
  cancelLabel?: string;
  busy?: boolean;
  error?: string | null;
  onCancel: () => void;
  onConfirm: () => void;
}

export default function ConfirmDialog({
  open,
  title,
  description,
  warningNote,
  checkboxLabel,
  checkboxChecked = false,
  onCheckboxChange,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  busy = false,
  error = null,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  const titleId = useId();
  const descId = useId();
  const cancelBtnRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!open) return;
    cancelBtnRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape" && !busy) {
        onCancel();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, busy, onCancel]);

  if (!open) return null;

  return (
    <div
      className="pm-dialog-backdrop"
      role="presentation"
      onClick={(e) => {
        if (e.target === e.currentTarget && !busy) {
          onCancel();
        }
      }}
    >
      <div
        className="pm-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descId}
      >
        <h2 id={titleId} className="pm-dialog-title">
          {title}
        </h2>
        <p id={descId} className="pm-dialog-desc">
          {description}
        </p>

        {warningNote && <div className="pm-dialog-note">{warningNote}</div>}

        {checkboxLabel && onCheckboxChange && (
          <label className="pm-dialog-check">
            <input
              type="checkbox"
              checked={checkboxChecked}
              onChange={(e) => onCheckboxChange(e.target.checked)}
              disabled={busy}
            />
            <span>{checkboxLabel}</span>
          </label>
        )}

        {error && (
          <p className="pm-dialog-error" role="alert">
            {error}
          </p>
        )}

        <div className="pm-dialog-actions">
          <button
            ref={cancelBtnRef}
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={busy}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            className="btn btn-danger-solid"
            onClick={onConfirm}
            disabled={busy}
          >
            {busy ? "Deleting..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
