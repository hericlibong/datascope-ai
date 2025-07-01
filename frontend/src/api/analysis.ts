import { authFetch } from "@/api/auth";

export async function lancerAnalyse(data: any) {
  const response = await authFetch("http://localhost:8000/api/analysis/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error("Erreur lors du lancement de l’analyse");
  }
  return await response.json();
}
