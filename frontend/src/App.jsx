import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import PostDetailPage from "./pages/PostDetailPage.jsx";
import AdminDashboardPage from "./pages/AdminDashboardPage.jsx";
import SignupPage from "./pages/SignupPage.jsx";
import ExpensesPage from "./pages/ExpensesPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import RequireAdmin from "./components/RequireAdmin.jsx";

export default function App() {
  return (
    <div className="appRoot">
      <Navbar />
      <main className="page">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/post/:id" element={<PostDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AdminDashboardPage />
              </RequireAdmin>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

