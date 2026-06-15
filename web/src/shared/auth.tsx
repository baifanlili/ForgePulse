import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

interface AuthState {
  token: string | null;
  username: string | null;
  displayName: string | null;
  role: string | null;
  login: (token: string, username: string, displayName: string, role: string) => void;
  logout: () => void;
  isLoggedIn: boolean;
}

const AuthContext = createContext<AuthState | null>(null);

const STORAGE_KEY = "forgepulse_auth";

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function saveToStorage(token: string, username: string, displayName: string, role: string) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, username, displayName, role }));
}

function clearStorage() {
  localStorage.removeItem(STORAGE_KEY);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    const saved = loadFromStorage();
    if (saved?.token) {
      setToken(saved.token);
      setUsername(saved.username);
      setDisplayName(saved.displayName);
      setRole(saved.role);
    }
  }, []);

  const login = useCallback(
    (newToken: string, newUsername: string, newDisplayName: string, newRole: string) => {
      setToken(newToken);
      setUsername(newUsername);
      setDisplayName(newDisplayName);
      setRole(newRole);
      saveToStorage(newToken, newUsername, newDisplayName, newRole);
    },
    [],
  );

  const logout = useCallback(() => {
    setToken(null);
    setUsername(null);
    setDisplayName(null);
    setRole(null);
    clearStorage();
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      token,
      username,
      displayName,
      role,
      login,
      logout,
      isLoggedIn: !!token,
    }),
    [token, username, displayName, role, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
