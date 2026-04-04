import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { directLogin } from "../lib/directSignup.js";

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await directLogin(formData.username, formData.password);

      // Store user data and token
      localStorage.setItem("authToken", result.token);
      localStorage.setItem("currentUser", JSON.stringify(result.user));

      // Redirect based on user role
      if (result.user.is_admin) {
        navigate("/admin");
      } else {
        navigate("/expenses");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div style={{ maxWidth: '400px', padding: '2rem', width: '100%' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text)' }}>Login</h1>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label htmlFor="username" style={{ fontWeight: '600', color: 'var(--text)' }}>Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              style={{ 
                padding: '0.75rem', 
                border: '1px solid rgba(255, 255, 255, 0.1)', 
                borderRadius: '6px', 
                background: 'var(--card)', 
                color: 'var(--text)', 
                fontSize: '1rem' 
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label htmlFor="password" style={{ fontWeight: '600', color: 'var(--text)' }}>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              style={{ 
                padding: '0.75rem', 
                border: '1px solid rgba(255, 255, 255, 0.1)', 
                borderRadius: '6px', 
                background: 'var(--card)', 
                color: 'var(--text)', 
                fontSize: '1rem' 
              }}
            />
          </div>

          {error && (
            <div style={{ 
              padding: '0.75rem', 
              borderRadius: '6px', 
              background: 'rgba(255, 107, 107, 0.1)', 
              border: '1px solid var(--danger)', 
              color: 'var(--danger)', 
              textAlign: 'center' 
            }}>
              {error}
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading} 
            style={{ 
              padding: '0.75rem', 
              border: 'none', 
              borderRadius: '6px', 
              background: loading ? 'rgba(94, 234, 212, 0.6)' : 'var(--accent)', 
              color: 'var(--bg)', 
              fontWeight: '600', 
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.6 : 1
            }}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--muted)' }}>
            Don't have an account?{" "}
            <a href="/user-signup" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
              Sign up as User
            </a>
            {" or "}
            <a href="/admin-signup" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
              Sign up as Admin
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
