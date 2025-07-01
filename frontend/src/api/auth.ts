// src/api/auth.ts

// Récupère le token d’accès depuis localStorage
export function getAccessToken() {
    return localStorage.getItem('accessToken');
  }


// Stocke les tokens dans localStorage
export function setTokens(tokens: { access: string; refresh: string }, username: string) {
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
    localStorage.setItem('username', username);
  }

// Efface les tokens (pour logout ou session expirée)
export function clearTokens() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('username');
  }

// Récupère le username connecté
export function getUsername() {
  return localStorage.getItem('username');
}

// REGISTER : création de compte utilisateur
export async function register({ username, email, password }: { username: string; email: string; password: string }) {
    const response = await fetch('http://localhost:8000/api/users/register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }) // <-- on envoie aussi username
    });
  
    if (!response.ok) {
      let message = 'Erreur lors de l’inscription';
      try {
        const data = await response.json();
        message = data?.detail || JSON.stringify(data) || message;
      } catch {
        // ...
      }
      throw new Error(message);
    }
    return await response.json();
  }

// LOGIN : obtention des tokens après connexion
export async function login({ username, password }: { username: string; password: string }) {
    const response = await fetch('http://localhost:8000/api/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!response.ok) {
      let message = 'Erreur lors de la connexion';
      try {
        const data = await response.json();
        message = data?.detail || JSON.stringify(data) || message;
      } catch {}
      throw new Error(message);
    }
    const tokens = await response.json();
    setTokens(tokens, username); // Stockage direct après login réussi
    return tokens;
  }


// Appel API protégé qui gère l’expiration du token
export async function authFetch(input: RequestInfo, init?: RequestInit) {
  const accessToken = getAccessToken();
  const headers = new Headers(init?.headers || {});
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }
  const response = await fetch(input, { ...init, headers });
  if (response.status === 401) {
    clearTokens();
    window.location.href = '/login';
    return Promise.reject(new Error("Session expirée, veuillez vous reconnecter"));
  }
  return response;
}

