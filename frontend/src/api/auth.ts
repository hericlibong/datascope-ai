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
  