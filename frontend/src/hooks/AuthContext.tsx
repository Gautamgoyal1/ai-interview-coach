
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { AuthCredentials, User } from "../types/auth";
import * as authService from "../services/auth.service";
import { getAccessToken } from "../utils/storage";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (credentials: AuthCredentials) => Promise<User>;
  register: (credentials: AuthCredentials) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      const token = getAccessToken();

      if (!token) {
        if (!cancelled) setLoading(false);
        return;
      }

      try {
        const authenticatedUser = await authService.getCurrentUser();

        if (!cancelled) {
          setUser(authenticatedUser);
        }
      } catch {
        authService.logout();

        if (!cancelled) {
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void restoreSession();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (credentials: AuthCredentials) => {
    setLoading(true);
    try {
      const authenticatedUser = await authService.login(credentials);
      setUser(authenticatedUser);
      return authenticatedUser;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (credentials: AuthCredentials) => {
    setLoading(true);
    try {
      return await authService.register(credentials);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuthContext must be used inside AuthProvider.");
  }

  return context;
}
