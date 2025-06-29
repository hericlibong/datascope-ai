import React, { useState } from 'react';
import { register } from '../../api/auth';

export default function SignupForm({ onSuccess }: { onSuccess?: () => void }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false); // Ajout du state pour le succès

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register({ username, email, password });
      setLoading(false);
      setSuccess(true); // Affiche le message de succès
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 1500); // Attend 1,5 secondes avant de rediriger
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white shadow rounded-xl space-y-4">
      <h2 className="text-2xl font-bold text-center">Créer un compte</h2>
      <input
        type="text"
        placeholder="Nom d’utilisateur"
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
        className="w-full border px-3 py-2 rounded"
      />
      <input
        type="email"
        placeholder="Adresse e-mail"
        value={email}
        onChange={e => setEmail(e.target.value)}
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
      {success && (
        <div className="text-green-600 mb-4 text-center">
          Compte créé avec succès&nbsp;! Redirection vers la connexion…
        </div>
      )}
      {error && <div className="text-red-500">{error}</div>}
      <button
        type="submit"
        disabled={loading || success}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        {loading ? "Création en cours…" : "S’inscrire"}
      </button>
    </form>
  );
}
