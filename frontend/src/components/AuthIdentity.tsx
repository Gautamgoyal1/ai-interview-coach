/** Shared presentation only; account forms retain their own behavior. */
export default function AuthIdentity() {
  return (
    <aside className="auth-identity" aria-label="The PrepMate preparation studio">
      <p className="auth-identity-kicker">THE PREPARATION STUDIO</p>
      <h2>Make room for your next move.</h2>
      <p>
        A place to put your experience into words, work through the gaps, and
        prepare with intention.
      </p>
      <ol className="auth-identity-steps">
        <li>
          <span>01</span>
          <div>
            <strong>Find your starting point</strong>
            <small>Connect your resume to your target role.</small>
          </div>
        </li>
        <li>
          <span>02</span>
          <div>
            <strong>Rehearse the conversation</strong>
            <small>Practice technical and behavioral interviews.</small>
          </div>
        </li>
        <li>
          <span>03</span>
          <div>
            <strong>Refine your approach</strong>
            <small>Use feedback to focus your next attempt.</small>
          </div>
        </li>
      </ol>
    </aside>
  );
}
