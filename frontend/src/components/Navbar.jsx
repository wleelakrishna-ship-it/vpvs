import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Check if user is logged in
  const isLoggedIn = localStorage.getItem("authToken");
  const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
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
            className={location.pathname === "/" ? "active" : ""}
            to="/"
          >
            Posts
          </Link>

          <Link
            className={location.pathname === "/expenses" ? "active" : ""}
            to="/expenses"
          >
            Expenses
          </Link>

          {isLoggedIn ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>
                {currentUser.username} {currentUser.is_admin ? '(Admin)' : '(User)'}
              </span>
              <button 
                className="navButton" 
                type="button" 
                onClick={handleLogout}
                style={{
                  backgroundColor: '#ef4444',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Logout
              </button>
            </div>
          ) : (
            <>
              <Link 
                className="navButton" 
                to="/signup"
                style={{
                  backgroundColor: 'var(--accent)',
                  color: 'white',
                  border: 'none',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  textDecoration: 'none'
                }}
              >
                Sign Up
              </Link>
              <Link className="navButton" to="/login">
                Login
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

