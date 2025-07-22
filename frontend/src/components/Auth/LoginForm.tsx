import React, { useState } from 'react';
import { login } from '../../api/auth';

type LoginFormProps = {
  onSuccess?: () => void;
  language: "en" | "fr";
  message?: string | null;
};

const TEXTS = {
  en: {
    title: "Login",
    username: "Username",
    password: "Password",
    error: "Invalid credentials",
    loading: "Logging in…",
    submit: "Login"
  },
  fr: {
    title: "Connexion",
    username: "Nom d’utilisateur",
    password: "Mot de passe",
    error: "Identifiants invalides",
    loading: "Connexion en cours…",
    submit: "Se connecter"
  }
};

export default function LoginForm({ onSuccess, language, message }: LoginFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const t = TEXTS[language];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ username, password }); // Token stocké automatiquement
      setLoading(false);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white shadow rounded-xl space-y-4">
      <h2 className="text-2xl font-bold text-center">{t.title}</h2>
      {message && (
        <div className="text-blue-600 text-center">{message}</div>
      )}
      <input
        type="text"
        placeholder={t.username}
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
        className="w-full border px-3 py-2 rounded"
      />
      <input
        type="password"
        placeholder={t.password}
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
        {loading ? t.loading : t.submit}
      </button>
    </form>
  );
}
