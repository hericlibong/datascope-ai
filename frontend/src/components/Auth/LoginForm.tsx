import React, { useState } from 'react';
import { login } from '../../api/auth';

export default function LoginForm({ onSuccess }: { onSuccess?: (tokens: any) => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await login({ username, password });
      setLoading(false);
      if (onSuccess) onSuccess(tokens); // On pourra stocker le token plus tard ici
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white shadow rounded-xl space-y-4">
      <h2 className="text-2xl font-bold text-center">Connexion</h2>
      <input
        type="text"
        placeholder="Nom d’utilisateur"
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
        className="w-full border px-3 py-2 rounded"
      />
      <input
        type="password"
        placeholder="Mot de passe"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
        className="w-full border px-3 py-2 rounded"
      />
      {error && <div className="text-red-500">{error}</div>}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        {loading ? "Connexion en cours…" : "Se connecter"}
      </button>
    </form>
  );
}
