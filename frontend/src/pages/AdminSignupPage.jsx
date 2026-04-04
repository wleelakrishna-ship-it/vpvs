import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { directSignup } from "../lib/directSignup.js";

export default function AdminSignupPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    phone: "",
    dob: "",
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
      const result = await directSignup({
        ...formData,
        is_admin: true,
      });

      // Store user data and token
      localStorage.setItem("authToken", result.token);
      localStorage.setItem("currentUser", JSON.stringify(result.user));

      // Redirect to admin dashboard
      navigate("/admin");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <div style={{ maxWidth: '400px', padding: '2rem', width: '100%' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text)' }}>Admin Sign Up</h1>
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

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label htmlFor="password" style={{ fontWeight: '600', color: 'var(--text)' }}>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={6}
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
            <label htmlFor="phone" style={{ fontWeight: '600', color: 'var(--text)' }}>Phone Number</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              pattern="[0-9]{10}"
              placeholder="1234567890"
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
            <label htmlFor="dob" style={{ fontWeight: '600', color: 'var(--text)' }}>Date of Birth</label>
            <input
              type="date"
              id="dob"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
              required
              max={new Date().toISOString().split('T')[0]}
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
            {loading ? "Signing up..." : "Sign Up as Admin"}
          </button>
        </form>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <p style={{ color: 'var(--muted)' }}>
            Already have an account?{" "}
            <a href="/admin/login" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
              Log in
            </a>
          </p>
          <p style={{ color: 'var(--muted)', marginTop: '0.5rem' }}>
            User signup?{" "}
            <a href="/user-signup" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
              Sign up as User
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
