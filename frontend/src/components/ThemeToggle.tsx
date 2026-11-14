import { MoonIcon, SunIcon } from "./Icons";
import { useTheme } from "../context/ThemeContext";
import "./ThemeToggle.css";

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

export default function ThemeToggle({
  className = "",
  showLabel = false,
}: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      className={`theme-toggle-btn ${className}`}
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
      title={`Switch to ${isDark ? "light" : "dark"} mode`}
    >
      <span className="theme-toggle-icon" aria-hidden="true">
        {isDark ? <SunIcon size={17} /> : <MoonIcon size={17} />}
      </span>
      {showLabel && (
        <span className="theme-toggle-label">
          {isDark ? "Light mode" : "Dark mode"}
        </span>
      )}
    </button>
  );
}
