
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import "./Layout.css";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">P</div>
          <div>
            <h2>PrepMate</h2>
            <p>AI Interview Coach</p>
          </div>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="nav-icon">▤</span>
            <span>Resume Analyzer</span>
          </NavLink>

          <div className="sidebar-link disabled-link" aria-disabled="true">
            <span className="nav-icon">◉</span>
            <span className="nav-link-label">Virtual Interview</span>
            <span className="coming-soon">SOON</span>
          </div>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-plan">
            <div className="plan-icon">✦</div>
            <div>
              <strong>Interview ready?</strong>
              <p>Prepare with confidence.</p>
            </div>
          </div>

          <button className="logout-button" onClick={handleLogout}>
            <span className="logout-icon">↪</span>
            Logout
          </button>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-separator">/</span>
            <strong>Resume Analyzer</strong>
          </div>

          <div className="profile">
            <div className="profile-avatar">
              {(user?.email?.[0] ?? "U").toUpperCase()}
            </div>
            <div className="profile-details">
              <strong>{user?.email ?? "User"}</strong>
              <span>Personal workspace</span>
            </div>
          </div>
        </header>

        <main className="workspace">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
