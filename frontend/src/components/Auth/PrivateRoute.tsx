// src/components/Auth/PrivateRoute.tsx

import { Navigate, Outlet } from "react-router-dom";
import { getAccessToken } from "@/api/auth";

// Ce composant protège les routes sensibles
export default function PrivateRoute() {
  const token = getAccessToken();

  // Si aucun token => redirection vers /login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Sinon on rend la page protégée (Outlet = contenu de la route)
  return <Outlet />;
}
