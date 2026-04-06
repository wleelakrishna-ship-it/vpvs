import React from "react";
import { Navigate } from "react-router-dom";

export default function RequireAdmin({ children }) {
  const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
  const authToken = localStorage.getItem("authToken");
  
  if (!authToken || !currentUser.is_admin) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

