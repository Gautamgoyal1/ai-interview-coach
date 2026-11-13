import { useState, type DragEvent } from "react";
import { CheckCircleIcon, UploadCloudIcon } from "./Icons";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

interface FileUploadProps {
  file: File | null;
  fileError: string | null;
  onSelect: (file: File | null, error: string | null) => void;
}

export default function FileUpload({
  file,
  fileError,
  onSelect,
}: FileUploadProps) {
  const [dragging, setDragging] = useState(false);

  function validateAndEmit(selected: File | null) {
    if (!selected) {
      onSelect(null, null);
      return;
    }

    const isPdf =
      selected.type === "application/pdf" ||
      selected.name.toLowerCase().endsWith(".pdf");

    if (!isPdf) {
      onSelect(null, "Please select a valid PDF file (.pdf).");
      return;
    }

    if (selected.size > MAX_FILE_SIZE) {
      onSelect(null, "Resume PDF must be 10 MB or smaller.");
      return;
    }

    onSelect(selected, null);
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer.files?.[0] ?? null;
    validateAndEmit(dropped);
  }

  return (
    <div className="upload-wrapper">
      <label
        htmlFor="resume-file"
        className={`upload-dropzone ${dragging ? "is-dragging" : ""} ${
          file ? "has-file" : ""
        } ${fileError ? "has-error" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input
          id="resume-file"
          type="file"
          accept="application/pdf,.pdf"
          className="upload-input-sr"
          onChange={(e) => validateAndEmit(e.target.files?.[0] ?? null)}
        />

        <div className="upload-icon-box">
          {file ? (
            <CheckCircleIcon size={20} />
          ) : (
            <UploadCloudIcon size={20} />
          )}
        </div>

        <div className="upload-copy">
          {file ? (
            <>
              <strong>{file.name}</strong>
              <span>
                {(file.size / 1024).toFixed(0)} KB · Click or drop another PDF to
                replace
              </span>
            </>
          ) : (
            <>
              <strong>Click to upload or drag and drop your PDF</strong>
              <span>PDF only · Maximum 10 MB</span>
            </>
          )}
        </div>
      </label>

      {fileError && (
        <p className="field-error" role="alert">
          {fileError}
        </p>
      )}
    </div>
  );
}
