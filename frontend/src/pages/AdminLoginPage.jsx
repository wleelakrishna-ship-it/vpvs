import React, { useMemo, useState } from "react";
import { createClient } from "@supabase/supabase-js";
import { useNavigate } from "react-router-dom";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";

export default function AdminLoginPage() {
  const navigate = useNavigate();
  const { setToken } = useAdminAuth();

  const supabase = useMemo(() => {
    const url = import.meta.env.VITE_SUPABASE_URL;
    const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
    if (!url || !anonKey) return null;
    return createClient(url, anonKey, {
      auth: { persistSession: true },
    });
  }, []);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleLogin(e) {
    e.preventDefault();
    setError(null);

    if (!supabase) {
      setError("Supabase env vars missing (VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY).");
      return;
    }

    try {
      setLoading(true);
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (signInError) throw signInError;
      const session = data?.session;
      if (!session?.access_token) throw new Error("Login succeeded but token missing");

      const user = session.user;
      const role =
        user?.app_metadata?.role ??
        user?.user_metadata?.role ??
        (Array.isArray(user?.app_metadata?.roles) ? user.app_metadata.roles[0] : null);
      const rolesArray = Array.isArray(user?.app_metadata?.roles) ? user.app_metadata.roles : [];
      const isAdmin = role === "admin" || rolesArray.includes("admin");
      if (!isAdmin) {
        await supabase.auth.signOut();
        throw new Error("You are not authorized as admin");
      }

      setToken(session.access_token);
      navigate("/admin");
    } catch (err) {
      setError(err.message || "Admin login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="form" style={{ maxWidth: 520, margin: "0 auto" }}>
      <div className="sectionTitle" style={{ marginTop: 0 }}>
        Admin Login
      </div>
      <form onSubmit={handleLogin}>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        {error ? <div className="smallNote" style={{ color: "#ff9aa2" }}>{error}</div> : null}
        <div className="btnRow">
          <button className="navButton primaryButton" type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </div>
        <div className="smallNote" style={{ marginTop: 12 }}>
          Admins must have auth metadata role = <code>admin</code>.
        </div>
      </form>
    </section>
  );
}

