import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

const AdminAuthContext = createContext(null);

const STORAGE_KEY = "antiGravity_admin_access_token";

export function AdminAuthProvider({ children }) {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const existing = window.localStorage.getItem(STORAGE_KEY);
    if (existing) setToken(existing);
  }, []);

  const value = useMemo(() => {
    return {
      token,
      setToken: (nextToken) => {
        if (nextToken) {
          window.localStorage.setItem(STORAGE_KEY, nextToken);
          setToken(nextToken);
        } else {
          window.localStorage.removeItem(STORAGE_KEY);
          setToken(null);
        }
      },
      logout: () => {
        window.localStorage.removeItem(STORAGE_KEY);
        setToken(null);
      },
    };
  }, [token]);

  return <AdminAuthContext.Provider value={value}>{children}</AdminAuthContext.Provider>;
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext);
  if (!ctx) throw new Error("useAdminAuth must be used within AdminAuthProvider");
  return ctx;
}

