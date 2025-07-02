// frontend/src/api/history.ts

import { authFetch } from "@/api/auth";

/**
 * Récupère l’historique des analyses de l’utilisateur courant.
 * @returns Un tableau d’analyses JSON
 */
export async function getUserHistory() {
  const response = await authFetch("http://localhost:8000/api/history/");
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération de l’historique.");
  }
  return await response.json();
}
