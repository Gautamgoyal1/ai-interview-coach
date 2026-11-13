
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./hooks/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ResumeAnalysis from "./pages/ResumeAnalysis";
import History from "./pages/History";
import InterviewRoom from "./pages/InterviewRoom";
import PracticeWorkspace from "./pages/PracticeWorkspace";
import Report from "./pages/Report";

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Authenticated Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/analyze" element={<ResumeAnalysis />} />
                <Route path="/history" element={<History />} />
                <Route path="/history/:analysisId" element={<History />} />
                <Route path="/interview" element={<InterviewRoom />} />
                <Route path="/interview/:sessionId" element={<InterviewRoom />} />
                <Route path="/reports" element={<Report />} />
                <Route path="/reports/:sessionId" element={<Report />} />
                <Route path="/practice" element={<PracticeWorkspace />} />
                <Route path="/practice/:sessionId" element={<PracticeWorkspace />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
