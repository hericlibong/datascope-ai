// src/api/analysis.ts

import { authFetch } from "@/api/auth";

/**
 * Lance une analyse via l'API protégée JWT
 * @param data Données de l'article à analyser (objet)
 * @returns Résultat de l'analyse (objet JSON)
 * @throws {Error} En cas d'échec (auth, validation, etc.)
 */
export async function lancerAnalyse(data: any) {
  try {
    const response = await authFetch("http://localhost:8000/api/analysis/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (response.status === 401) {
      // Ce cas est déjà géré dans authFetch (redirection login)
      throw new Error("Votre session a expiré. Merci de vous reconnecter.");
    }

    if (!response.ok) {
      let errorMsg = "Erreur lors du lancement de l’analyse";
      try {
        const backendError = await response.json();
        // On tente d’afficher une erreur lisible du backend si dispo
        errorMsg = backendError?.detail || errorMsg;
      } catch {
        // Si le backend ne renvoie pas de JSON
      }
      throw new Error(errorMsg);
    }

    // Tout s’est bien passé : on retourne le résultat
    return await response.json();

  } catch (error: any) {
    // Gestion centralisée de l’erreur (propagation)
    throw new Error(error.message || "Erreur inconnue lors du lancement de l’analyse.");
  }
}
