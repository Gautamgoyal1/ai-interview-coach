import { useEffect, useRef, useState } from "react";
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
  UserIcon,
  XIcon,
} from "./Icons";
import ThemeToggle from "./ThemeToggle";
import "./Layout.css";
import { useModalFocus } from "../hooks/useModalFocus";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: DashboardIcon, end: true },
  { to: "/analyze", label: "Resume Analyzer", icon: FileTextIcon, end: false },
  { to: "/history", label: "Analysis History", icon: HistoryIcon, end: false },
  { to: "/interview", label: "AI Interview", icon: MessageSquareIcon, end: false },
  { to: "/reports", label: "Interview Reports", icon: BarChartIcon, end: false },
  { to: "/practice", label: "Practice Mode", icon: BookOpenIcon, end: false },
  { to: "/profile", label: "Profile & Settings", icon: UserIcon, end: false },
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
                  : location.pathname === "/profile"
                    ? "Profile & Settings"
                    : "Dashboard";

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const sidebarRef = useRef<HTMLElement | null>(null);
  const [mobile, setMobile] = useState(() => window.matchMedia("(max-width: 960px)").matches);
  useModalFocus(mobile && mobileMenuOpen, sidebarRef, () => setMobileMenuOpen(false));
  useEffect(() => {
    const query = window.matchMedia("(max-width: 960px)");
    const update = () => { setMobile(query.matches); if (!query.matches) setMobileMenuOpen(false); };
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  useEffect(() => { if (sidebarRef.current) sidebarRef.current.inert = mobile && !mobileMenuOpen; }, [mobile, mobileMenuOpen]);

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
          data-modal-backdrop
          onClick={() => setMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        ref={sidebarRef}
        role={mobile && mobileMenuOpen ? "dialog" : undefined}
        aria-modal={mobile && mobileMenuOpen ? true : undefined}
        tabIndex={-1}
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
          <div className={`sidebar-user-card ${location.pathname === "/profile" ? "active" : ""}`}>
          <NavLink to="/profile" className="sidebar-profile-link" title="View and edit profile">
            <div className="profile-avatar">
              {(user?.full_name?.trim()?.[0] || user?.email?.[0] || "U").toUpperCase()}
            </div>
            <div className="profile-details">
              <strong title={user?.full_name?.trim() || user?.email || "User"}>
                {user?.full_name?.trim() || user?.email || "User"}
              </strong>
              <span
                className={!user?.target_role && user?.email ? "profile-email" : undefined}
                title={!user?.target_role ? user?.email : undefined}
              >{user?.target_role || user?.email || "Personal workspace"}</span>
            </div>
          </NavLink>
          <div className="sidebar-user-action"><ThemeToggle className="sidebar-theme-toggle" /></div>
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
            <ThemeToggle />
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
