import { useState, type FormEvent, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../context/ThemeContext";
import {
  CheckCircleIcon,
  CheckIcon,
  EyeIcon,
  EyeOffIcon,
  KeyIcon,
  LockIcon,
  LogOutIcon,
  MailIcon,
  MoonIcon,
  ShieldCheckIcon,
  SparklesIcon,
  SunIcon,
  TargetIcon,
  UserIcon,
} from "../components/Icons";
import "./Profile.css";

const COMMON_ROLE_SUGGESTIONS = [
  "Full-Stack Engineer",
  "Backend Engineer",
  "Frontend Engineer",
  "System Design Specialist",
  "DevOps & Cloud Engineer",
  "Product Manager",
  "Data Scientist",
];

const EXPERIENCE_LEVELS = [
  {
    key: "internship",
    title: "Internship / Student",
    description: "Foundational concepts, CS basics, academic projects",
  },
  {
    key: "fresher",
    title: "Fresher / Entry-Level",
    description: "0–1 years. Strong programming fundamentals & core systems",
  },
  {
    key: "intermediate",
    title: "Intermediate",
    description: "2–4 years. Production features, debugging, and trade-offs",
  },
  {
    key: "experienced",
    title: "Experienced / Senior",
    description: "5+ years. Distributed systems, architectural depth, and leadership",
  },
];

export default function Profile() {
  const { user, updateProfile, changePassword, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();

  // Profile Information Form State
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [targetRole, setTargetRole] = useState(user?.target_role || "");
  const [experienceLevel, setExperienceLevel] = useState(
    user?.experience_level || "intermediate"
  );
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState("");
  const [profileError, setProfileError] = useState("");

  // Sync state if user updates
  useEffect(() => {
    if (user) {
      if (user.full_name !== undefined) setFullName(user.full_name || "");
      if (user.target_role !== undefined) setTargetRole(user.target_role || "");
      if (user.experience_level !== undefined && user.experience_level) {
        setExperienceLevel(user.experience_level);
      }
    }
  }, [user]);

  // Password Security Form State
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordError, setPasswordError] = useState("");

  // Handle Profile Update
  async function handleProfileSubmit(e: FormEvent) {
    e.preventDefault();
    setProfileSuccess("");
    setProfileError("");
    setProfileSaving(true);

    try {
      await updateProfile({
        full_name: fullName.trim() || undefined,
        target_role: targetRole.trim() || undefined,
        experience_level: experienceLevel || undefined,
      });
      setProfileSuccess("Profile updated successfully!");
      setTimeout(() => setProfileSuccess(""), 4500);
    } catch (err) {
      setProfileError(
        err instanceof Error ? err.message : "Failed to update profile."
      );
    } finally {
      setProfileSaving(false);
    }
  }

  // Handle Password Change
  async function handlePasswordSubmit(e: FormEvent) {
    e.preventDefault();
    setPasswordSuccess("");
    setPasswordError("");

    if (!currentPassword) {
      setPasswordError("Please enter your current password.");
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters long.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("New passwords do not match.");
      return;
    }

    if (newPassword === currentPassword) {
      setPasswordError("New password must be different from current password.");
      return;
    }

    setPasswordSaving(true);

    try {
      const res = await changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordSuccess(
        res.message || "Password updated successfully! Keep your credentials safe."
      );
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPasswordSuccess(""), 5500);
    } catch (err) {
      setPasswordError(
        err instanceof Error ? err.message : "Failed to change password."
      );
    } finally {
      setPasswordSaving(false);
    }
  }

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  const userInitial = (
    user?.full_name?.trim()?.[0] ||
    user?.email?.[0] ||
    "U"
  ).toUpperCase();

  const formattedJoinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
      })
    : "November 2026";

  const isPasswordLengthMet = newPassword.length >= 8;
  const isPasswordMatch =
    newPassword.length > 0 && newPassword === confirmPassword;

  return (
    <div className="profile-page">
      {/* Page Header */}
      <div className="pm-page-header">
        <div>
          <p className="pm-eyebrow">Account & Workspace</p>
          <h1 className="pm-page-title">Profile & Settings</h1>
          <p className="pm-page-subtitle">
            Manage your personal profile, calibration preferences, security
            credentials, and workspace theme.
          </p>
        </div>
      </div>

      {/* Hero Profile Overview Card */}
      <section className="profile-hero-card" aria-label="Profile overview">
        <div className="profile-hero-left">
          <div className="profile-hero-avatar">{userInitial}</div>
          <div className="profile-hero-meta">
            <h2 className="profile-hero-name">
              {user?.full_name?.trim() || "PrepMate Member"}
            </h2>
            <div className="profile-hero-tags">
              <span className="badge badge-accent">
                {user?.target_role || "Role: General Tech"}
              </span>
              <span className="badge badge-neutral">
                {user?.experience_level
                  ? user.experience_level.charAt(0).toUpperCase() +
                    user.experience_level.slice(1)
                  : "Intermediate"}
              </span>
            </div>
            <div className="profile-hero-email">
              <MailIcon size={14} />
              <span>{user?.email}</span>
            </div>
          </div>
        </div>

        <div className="profile-hero-right">
          <div className="profile-hero-stat-badge">
            <span className="profile-hero-stat-dot" />
            <span>Active Account</span>
          </div>
          <span className="profile-hint">Joined {formattedJoinDate}</span>
        </div>
      </section>

      {/* Two-Column Core Form Grid */}
      <div className="profile-grid">
        {/* Card 1: Personal Details & Interview Calibration */}
        <section className="profile-card" aria-label="Personal information">
          <div className="profile-card-header">
            <div className="profile-card-icon-wrap">
              <UserIcon size={20} />
            </div>
            <div className="profile-card-titles">
              <h2>Personal & Role Calibration</h2>
              <p>
                Update your display name and interview target role. PrepMate uses
                these to adjust question rubrics.
              </p>
            </div>
          </div>

          <form onSubmit={handleProfileSubmit} className="profile-form">
            {profileSuccess && (
              <div
                className="profile-alert profile-alert-success"
                role="status"
              >
                <CheckCircleIcon size={18} />
                <span>{profileSuccess}</span>
              </div>
            )}

            {profileError && (
              <div className="profile-alert profile-alert-error" role="alert">
                <span>{profileError}</span>
              </div>
            )}

            {/* Full Name */}
            <div className="profile-form-group">
              <label htmlFor="full_name" className="profile-label">
                <span>Full Name</span>
                <span className="profile-label-badge">Visible in dashboard</span>
              </label>
              <div className="profile-input-wrapper">
                <span className="profile-input-icon">
                  <UserIcon size={16} />
                </span>
                <input
                  id="full_name"
                  type="text"
                  className="profile-input has-left-icon"
                  placeholder="e.g. Alex Morgan"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  maxLength={120}
                />
              </div>
              <span className="profile-hint">
                How PrepMate greets you across your workspace.
              </span>
            </div>

            {/* Email (Read Only) */}
            <div className="profile-form-group">
              <label htmlFor="email" className="profile-label">
                <span>Email Address</span>
                <span className="badge badge-success">Verified</span>
              </label>
              <div className="profile-input-wrapper">
                <span className="profile-input-icon">
                  <MailIcon size={16} />
                </span>
                <input
                  id="email"
                  type="email"
                  className="profile-input has-left-icon"
                  value={user?.email || ""}
                  readOnly
                  disabled
                />
              </div>
              <span className="profile-hint">
                Email address is permanently tied to your account authentication.
              </span>
            </div>

            {/* Target Role */}
            <div className="profile-form-group">
              <label htmlFor="target_role" className="profile-label">
                <span>Target Role</span>
                <span className="profile-label-badge">Calibration</span>
              </label>
              <div className="profile-input-wrapper">
                <span className="profile-input-icon">
                  <TargetIcon size={16} />
                </span>
                <input
                  id="target_role"
                  type="text"
                  className="profile-input has-left-icon"
                  placeholder="e.g. Senior Backend Engineer"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  maxLength={120}
                />
              </div>
              {/* Quick suggestions */}
              <div className="profile-role-chips">
                {COMMON_ROLE_SUGGESTIONS.map((role) => (
                  <button
                    key={role}
                    type="button"
                    className={`profile-role-chip ${
                      targetRole === role ? "active" : ""
                    }`}
                    onClick={() => setTargetRole(role)}
                  >
                    {role}
                  </button>
                ))}
              </div>
            </div>

            {/* Experience Level Selector */}
            <div className="profile-form-group">
              <label className="profile-label">
                <span>Experience Level</span>
                <span className="profile-label-badge">Question Rubric</span>
              </label>
              <div className="experience-level-grid">
                {EXPERIENCE_LEVELS.map((lvl) => (
                  <div
                    key={lvl.key}
                    className={`experience-level-card ${
                      experienceLevel === lvl.key ? "selected" : ""
                    }`}
                    onClick={() => setExperienceLevel(lvl.key)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        setExperienceLevel(lvl.key);
                      }
                    }}
                  >
                    <div className="experience-level-title">
                      <span>{lvl.title}</span>
                      {experienceLevel === lvl.key && (
                        <CheckIcon size={15} className="experience-selected-check" />
                      )}
                    </div>
                    <span className="experience-level-desc">{lvl.description}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={profileSaving}
              style={{ marginTop: 8 }}
            >
              {profileSaving ? (
                <>
                  <span className="spinner-border spinner-border-sm" />
                  <span>Saving Changes...</span>
                </>
              ) : (
                <>
                  <CheckIcon size={16} />
                  <span>Save Profile</span>
                </>
              )}
            </button>
          </form>
        </section>

        {/* Card 2: Security & Password Management */}
        <section className="profile-card" aria-label="Password and security">
          <div className="profile-card-header">
            <div className="profile-card-icon-wrap">
              <LockIcon size={20} />
            </div>
            <div className="profile-card-titles">
              <h2>Security & Password</h2>
              <p>
                Change your account password securely. We recommend using a unique,
                strong passphrase.
              </p>
            </div>
          </div>

          <form onSubmit={handlePasswordSubmit} className="profile-form">
            {passwordSuccess && (
              <div
                className="profile-alert profile-alert-success"
                role="status"
              >
                <CheckCircleIcon size={18} />
                <span>{passwordSuccess}</span>
              </div>
            )}

            {passwordError && (
              <div className="profile-alert profile-alert-error" role="alert">
                <span>{passwordError}</span>
              </div>
            )}

            {/* Current Password */}
            <div className="profile-form-group">
              <label htmlFor="current_password" className="profile-label">
                <span>Current Password</span>
              </label>
              <div className="profile-input-wrapper">
                <span className="profile-input-icon">
                  <KeyIcon size={16} />
                </span>
                <input
                  id="current_password"
                  type={showCurrentPassword ? "text" : "password"}
                  className="profile-input has-left-icon has-right-icon"
                  placeholder="Enter your current password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="profile-input-toggle"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  aria-label={
                    showCurrentPassword ? "Hide password" : "Show password"
                  }
                >
                  {showCurrentPassword ? (
                    <EyeOffIcon size={16} />
                  ) : (
                    <EyeIcon size={16} />
                  )}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div className="profile-form-group">
              <label htmlFor="new_password" className="profile-label">
                <span>New Password</span>
              </label>
              <div className="profile-input-wrapper">
                <span className="profile-input-icon">
                  <LockIcon size={16} />
                </span>
                <input
                  id="new_password"
                  type={showNewPassword ? "text" : "password"}
                  className="profile-input has-left-icon has-right-icon"
                  placeholder="At least 8 characters"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  className="profile-input-toggle"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  aria-label={
                    showNewPassword ? "Hide password" : "Show password"
                  }
                >
                  {showNewPassword ? (
                    <EyeOffIcon size={16} />
                  ) : (
                    <EyeIcon size={16} />
                  )}
                </button>
              </div>
            </div>

            {/* Confirm New Password */}
            <div className="profile-form-group">
              <label htmlFor="confirm_password" className="profile-label">
                <span>Confirm New Password</span>
              </label>
              <div className="profile-input-wrapper">
                <span className="profile-input-icon">
                  <LockIcon size={16} />
                </span>
                <input
                  id="confirm_password"
                  type={showConfirmPassword ? "text" : "password"}
                  className="profile-input has-left-icon has-right-icon"
                  placeholder="Re-enter new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  className="profile-input-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={
                    showConfirmPassword ? "Hide password" : "Show password"
                  }
                >
                  {showConfirmPassword ? (
                    <EyeOffIcon size={16} />
                  ) : (
                    <EyeIcon size={16} />
                  )}
                </button>
              </div>
            </div>

            {/* Real-time Checklist */}
            <div className="password-requirements">
              <span className="password-requirements-title">Requirements</span>
              <div
                className={`password-req-item ${
                  isPasswordLengthMet ? "met" : "unmet"
                }`}
              >
                {isPasswordLengthMet ? (
                  <CheckIcon size={14} />
                ) : (
                  <span style={{ width: 14 }}>•</span>
                )}
                <span>Minimum 8 characters in length</span>
              </div>
              <div
                className={`password-req-item ${
                  isPasswordMatch ? "met" : "unmet"
                }`}
              >
                {isPasswordMatch ? (
                  <CheckIcon size={14} />
                ) : (
                  <span style={{ width: 14 }}>•</span>
                )}
                <span>Passwords match</span>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-secondary"
              disabled={passwordSaving || !currentPassword || !newPassword}
              style={{ marginTop: 8 }}
            >
              {passwordSaving ? (
                <>
                  <span className="spinner-border spinner-border-sm" />
                  <span>Updating Password...</span>
                </>
              ) : (
                <>
                  <ShieldCheckIcon size={16} />
                  <span>Update Password</span>
                </>
              )}
            </button>
          </form>
        </section>
      </div>

      {/* Card 3: Workspace Theme & Display Preferences */}
      <section className="profile-card" aria-label="Theme and preferences">
        <div className="profile-card-header">
          <div className="profile-card-icon-wrap">
            <SparklesIcon size={20} />
          </div>
          <div className="profile-card-titles">
            <h2>Workspace Appearance</h2>
            <p>
              Choose how PrepMate looks to you. Seamlessly switch between Warm
              Editorial Cream and Nighttime Charcoal.
            </p>
          </div>
        </div>

        <div className="theme-picker-grid">
          {/* Light Mode Option */}
          <div
            className={`theme-card-option ${theme === "light" ? "active" : ""}`}
            onClick={() => setTheme("light")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") setTheme("light");
            }}
          >
            <div className="theme-preview-box light-mode-preview">
              <div className="theme-mini-row">
                <span
                  className="theme-mini-dot"
                  style={{ background: "#C65D3B" }}
                />
                <span
                  className="theme-mini-dot"
                  style={{ background: "#202C39" }}
                />
              </div>
              <div
                className="theme-mini-bar"
                style={{ background: "#E8E0D3" }}
              />
            </div>
            <div className="theme-card-label">
              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <SunIcon size={16} />
                <span>Warm Editorial (Light)</span>
              </div>
              {theme === "light" && <CheckIcon size={15} color="var(--accent)" />}
            </div>
          </div>

          {/* Dark Mode Option */}
          <div
            className={`theme-card-option ${theme === "dark" ? "active" : ""}`}
            onClick={() => setTheme("dark")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") setTheme("dark");
            }}
          >
            <div className="theme-preview-box dark-mode-preview">
              <div className="theme-mini-row">
                <span
                  className="theme-mini-dot"
                  style={{ background: "#D97757" }}
                />
                <span
                  className="theme-mini-dot"
                  style={{ background: "#F0EAE1" }}
                />
              </div>
              <div
                className="theme-mini-bar"
                style={{ background: "#2E2E2E" }}
              />
            </div>
            <div className="theme-card-label">
              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <MoonIcon size={16} />
                <span>Espresso Charcoal (Dark)</span>
              </div>
              {theme === "dark" && <CheckIcon size={15} color="var(--accent)" />}
            </div>
          </div>
        </div>
      </section>

      {/* Card 4: Danger Zone / Session Management */}
      <section className="profile-card danger-zone-card" aria-label="Danger zone">
        <div className="danger-zone-content">
          <div className="danger-zone-info">
            <h3>Active Session Management</h3>
            <p>
              Sign out of your active PrepMate session on this device.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-danger-outline"
            onClick={handleLogout}
          >
            <LogOutIcon size={16} />
            <span>Sign Out</span>
          </button>
        </div>
      </section>
    </div>
  );
}
