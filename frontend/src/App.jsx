import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import PostDetailPage from "./pages/PostDetailPage.jsx";
import AdminLoginPage from "./pages/AdminLoginPage.jsx";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import { AdminAuthProvider } from "./state/AdminAuthContext.jsx";
import RequireAdmin from "./components/RequireAdmin.jsx";

export default function App() {
  return (
    <AdminAuthProvider>
      <div className="appRoot">
        <Navbar />
        <main className="page">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/post/:id" element={<PostDetailPage />} />
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route
              path="/admin"
              element={
                <RequireAdmin>
                  <AdminDashboard />
                </RequireAdmin>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </AdminAuthProvider>
  );
}

