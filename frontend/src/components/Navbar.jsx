import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";

export default function Navbar() {
  const { token, logout } = useAdminAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  // Check if user is logged in
  const isLoggedIn = localStorage.getItem("authToken");
  const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    logout();
    navigate("/login");
  };

  return (
    <header className="navbar">
      <div className="navbarInner">
        <Link className="brand" to="/">
          VPVS
        </Link>

        <nav className="navLinks">
          {isLoggedIn && currentUser.is_admin && (
            <Link
              className={location.pathname.startsWith("/admin") ? "active" : ""}
              to="/admin"
              title="Admin dashboard"
            >
              Dashboard
            </Link>
          )}

          <Link
            className={location.pathname === "/expenses" ? "active" : ""}
            to="/expenses"
          >
            Expenses
          </Link>

          {isLoggedIn ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                {currentUser.username}
              </span>
              <button className="navButton" type="button" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <div style={{ position: 'relative' }}>
              <button
                style={{
                  backgroundColor: 'var(--accent)',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer'
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
                Sign Up
              </button>
              <div style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: '4px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                display: 'none',
                minWidth: '150px',
                zIndex: 1000
              }} className="signupDropdown"
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
                    padding: '0.5rem 1rem',
                    textDecoration: 'none',
                    color: 'var(--text)',
                    borderBottom: '1px solid var(--border)'
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
                    padding: '0.5rem 1rem',
                    textDecoration: 'none',
                    color: 'var(--text)'
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
          )}

          {!isLoggedIn && (
            <Link className="navButton" to="/login">
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

