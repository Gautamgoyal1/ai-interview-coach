import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import {
  BarChartIcon,
  BookOpenIcon,
  DashboardIcon,
  FileTextIcon,
  GraduationCapIcon,
  HistoryIcon,
  LogOutIcon,
  MenuIcon,
  MessageSquareIcon,
  XIcon,
} from "./Icons";
import "./Layout.css";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: DashboardIcon, end: true },
  { to: "/analyze", label: "Resume Analyzer", icon: FileTextIcon, end: false },
  { to: "/history", label: "Analysis History", icon: HistoryIcon, end: false },
  { to: "/interview", label: "AI Interview", icon: MessageSquareIcon, end: false },
  { to: "/reports", label: "Interview Reports", icon: BarChartIcon, end: false },
  { to: "/practice", label: "Practice Mode", icon: BookOpenIcon, end: false },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isFocusedInterview = /^\/interview\/[^/]+/.test(location.pathname);

  const breadcrumbLabel = location.pathname.startsWith("/history/")
    ? "Saved Analysis"
    : location.pathname === "/history"
      ? "Analysis History"
      : location.pathname.startsWith("/analyze")
        ? "Resume Analyzer"
        : location.pathname.startsWith("/interview")
          ? "AI Interview"
          : location.pathname.startsWith("/reports/")
            ? "Interview Report"
            : location.pathname === "/reports"
              ? "Interview Reports"
              : location.pathname.startsWith("/practice/")
                ? "Practice Studio"
                : location.pathname === "/practice"
                  ? "Practice Hub"
                  : "Dashboard";

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!mobileMenuOpen) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setMobileMenuOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [mobileMenuOpen]);

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  if (isFocusedInterview) {
    return (
      <div className="focused-shell">
        <main className="focused-workspace">
          <Outlet />
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {mobileMenuOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={`sidebar ${mobileMenuOpen ? "sidebar-open" : ""}`}
        aria-label="Primary sidebar"
      >
        <div className="sidebar-header">
          <NavLink to="/dashboard" className="sidebar-brand">
            <div className="brand-icon">
              <GraduationCapIcon size={19} />
            </div>
            <div className="brand-text">
              <h2>PrepMate</h2>
              <span className="brand-tag">Workspace</span>
            </div>
          </NavLink>

          <button
            type="button"
            className="mobile-close-btn"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation menu"
          >
            <XIcon size={18} />
          </button>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={17} className="nav-icon" />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-user-card">
            <div className="profile-avatar">
              {(user?.email?.[0] ?? "U").toUpperCase()}
            </div>
            <div className="profile-details">
              <strong title={user?.email ?? "User"}>
                {user?.email ?? "User"}
              </strong>
              <span>Personal workspace</span>
            </div>
          </div>

          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
            title="Sign out of PrepMate"
          >
            <LogOutIcon size={16} />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar-left">
            <button
              type="button"
              className="mobile-menu-btn"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation menu"
              aria-expanded={mobileMenuOpen}
            >
              <MenuIcon size={20} />
            </button>
            <nav className="breadcrumb" aria-label="Breadcrumb">
              <span>PrepMate</span>
              <span className="breadcrumb-separator">/</span>
              <strong>{breadcrumbLabel}</strong>
            </nav>
          </div>

          <div className="topbar-actions">
            {location.pathname !== "/analyze" && (
              <NavLink to="/analyze" className="btn btn-secondary topbar-cta">
                <FileTextIcon size={14} />
                <span>Analyze Resume</span>
              </NavLink>
            )}
          </div>
        </header>

        <main className="workspace">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
