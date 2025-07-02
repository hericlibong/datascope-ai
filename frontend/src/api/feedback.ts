// frontend/src/api/feedback.ts

import { getAccessToken } from "@/api/auth";

/**
 * Envoie un feedback utilisateur à l’API protégée JWT
 * @param data Objet contenant le feedback à soumettre
 * @returns Réponse JSON du backend
 * @throws {Error} Si l’envoi échoue (401 ou autre erreur)
 */
export async function envoyerFeedback(data: any) {
  const accessToken = getAccessToken();
  if (!accessToken) {
    throw new Error("Session expirée. Veuillez vous reconnecter.");
  }

  const response = await fetch("http://localhost:8000/api/feedbacks/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(data),
  });

  if (response.status === 401) {
    throw new Error("Session expirée. Veuillez vous reconnecter.");
  }

  if (!response.ok) {
    let message = "Erreur lors de l’envoi du feedback.";
    try {
      const detail = await response.json();
      message = detail?.detail || message;
    } catch {}
    throw new Error(message);
  }
  return await response.json();
}
