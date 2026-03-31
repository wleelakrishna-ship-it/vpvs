import React from "react";
import { Navigate } from "react-router-dom";
import { useAdminAuth } from "../state/AdminAuthContext.jsx";

export default function RequireAdmin({ children }) {
  const { token } = useAdminAuth();
  if (!token) return <Navigate to="/admin/login" replace />;
  return children;
}

