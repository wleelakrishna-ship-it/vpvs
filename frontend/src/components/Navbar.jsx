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
          Anti Gravity
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

