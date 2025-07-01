// Exemple dans src/api/user.ts
import { authFetch } from './auth';

export async function getUserHistory() {
  const res = await authFetch('http://localhost:8000/api/history/');
  if (!res.ok) throw new Error('Erreur lors de la récupération de l’historique');
  return await res.json();
}
