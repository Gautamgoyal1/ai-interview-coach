
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function ProtectedRoute() {
  const { user, loading, sessionError } = useAuth();

  // Wait for session restoration before deciding where to navigate.
  if (loading) {
    return <div>Restoring your session...</div>;
  }

  if (!user) {
    if (sessionError) return (
      <div className="container" role="alert">
        <p>{sessionError}</p>
        <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>Retry session</button>
      </div>
    );
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
