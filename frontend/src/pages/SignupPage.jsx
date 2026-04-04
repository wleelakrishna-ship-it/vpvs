import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SignupPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    is_admin: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/profiles/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Signup failed");
      }

      // Redirect to login page after successful signup
      navigate("/admin/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div style={{ maxWidth: '400px', padding: '2rem', width: '100%' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text)' }}>Sign Up</h1>
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
              maxLength={32}
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
            <label htmlFor="email" style={{ fontWeight: '600', color: 'var(--text)' }}>Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
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

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--text)' }}>
              <input
                type="checkbox"
                name="is_admin"
                checked={formData.is_admin}
                onChange={handleChange}
                style={{ width: 'auto' }}
              />
              Sign up as Admin
            </label>
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
            {loading ? "Signing up..." : "Sign Up"}
          </button>
        </form>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--muted)' }}>
            Already have an account?{" "}
            <a href="/admin/login" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
              Log in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
