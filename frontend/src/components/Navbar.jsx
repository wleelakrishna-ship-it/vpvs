import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";

export default function Navbar() {
  const { token, logout } = useAdminAuth();
  const location = useLocation();

  return (
    <header className="navbar">
      <div className="navbarInner">
        <Link className="brand" to="/">
          VPVS
        </Link>

        <nav className="navLinks">
          <Link
            className={location.pathname.startsWith("/admin") ? "active" : ""}
            to="/admin"
            title="Admin dashboard"
            aria-disabled={!token}
            onClick={(e) => {
              if (!token) e.preventDefault();
            }}
          >
            Dashboard
          </Link>

          <Link
            className={location.pathname === "/expenses" ? "active" : ""}
            to="/expenses"
          >
            Expenses
          </Link>

          <div style={{ position: 'relative' }}>
            <button
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text)',
                cursor: 'pointer',
                padding: '0.5rem',
                borderRadius: '4px'
              }}
              onMouseEnter={(e) => {
                const dropdown = e.currentTarget.nextElementSibling;
                if (dropdown) dropdown.style.display = 'block';
              }}
              onMouseLeave={(e) => {
                const dropdown = e.currentTarget.nextElementSibling;
                if (dropdown) dropdown.style.display = 'none';
              }}
            >
              Sign Up ▼
            </button>
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: '0',
                background: 'var(--card)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '4px',
                padding: '0.5rem',
                display: 'none',
                minWidth: '150px',
                zIndex: 1000
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.display = 'block';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.display = 'none';
              }}
            >
              <Link
                to="/admin-signup"
                style={{
                  display: 'block',
                  padding: '0.5rem',
                  color: 'var(--text)',
                  textDecoration: 'none',
                  borderRadius: '2px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'none';
                }}
              >
                Admin Signup
              </Link>
              <Link
                to="/user-signup"
                style={{
                  display: 'block',
                  padding: '0.5rem',
                  color: 'var(--text)',
                  textDecoration: 'none',
                  borderRadius: '2px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'none';
                }}
              >
                User Signup
              </Link>
            </div>
          </div>

          {token ? (
            <button className="navButton" type="button" onClick={logout}>
              Logout
            </button>
          ) : (
            <Link className="navButton" to="/admin/login">
              Admin Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

