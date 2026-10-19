
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Register() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (new TextEncoder().encode(password).length > 72) {
      setError("Password must not exceed 72 UTF-8 bytes.");
      return;
    }

    try {
      await register({ email: email.trim(), password });
      setSuccess("Account created successfully. Redirecting to sign in...");
      window.setTimeout(() => navigate("/login"), 1000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Registration failed.",
      );
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <Link to="/login" className="auth-brand">
          PrepMate
        </Link>

        <h1>Create your account</h1>
        <p className="auth-subtitle">
          Start preparing for interviews with confidence.
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          <label htmlFor="register-email">Email address</label>
          <input
            id="register-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
          />

          <label htmlFor="register-password">Password</label>
          <div className="password-field">
            <input
              id="register-password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 8 characters"
              minLength={8}
              maxLength={72}
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword((visible) => !visible)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          <label htmlFor="confirm-password">Confirm password</label>
          <input
            id="confirm-password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="Re-enter your password"
            required
          />

          {error && <p className="auth-error" role="alert">{error}</p>}
          {success && <p className="auth-success" role="status">{success}</p>}

          <button className="auth-submit" type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}
