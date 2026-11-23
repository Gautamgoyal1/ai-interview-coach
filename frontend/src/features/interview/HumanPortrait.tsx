import { useState } from "react";

type Role = "interviewer" | "candidate";

// These photographic poses are not registered facial layers or a rig. Blending
// their mouth/eyelid patches changes facial landmarks and lighting. Keep the
// original identity still; ActiveSpeakerStage owns the audio activity meter.
export default function HumanPortrait({ role }: { role: Role }) {
  const [failedRole, setFailedRole] = useState<Role | null>(null);
  const imageFailed = failedRole === role;
  return (
    <div className="iv-human-portrait" aria-hidden="true" data-renderer="static"
      data-mouth="closed" data-image-error={imageFailed}>
      {imageFailed ? (
        <span className="iv-human-fallback">{role === "interviewer" ? "AI interviewer" : "Your avatar"}</span>
      ) : (
        <img key={role} className="iv-human-still" src={`/avatars/${role}-neutral.webp`} alt=""
          width="480" height="600" decoding="async" draggable={false} onError={() => setFailedRole(role)} />
      )}
    </div>
  );
}
