import React, { useState } from 'react';
import { register } from '../../api/auth';

type SignupFormProps = {
  onSuccess?: () => void;
  language: "en" | "fr";
};

const TEXTS = {
  en: {
    title: "Sign up",
    username: "Username",
    email: "Email address",
    password: "Password",
    success: "Account created successfully! Redirecting to login…",
    error: "An error occurred.",
    loading: "Creating account…",
    submit: "Sign up"
  },
  fr: {
    title: "Créer un compte",
    username: "Nom d’utilisateur",
    email: "Adresse e-mail",
    password: "Mot de passe",
    success: "Compte créé avec succès ! Redirection vers la connexion…",
    error: "Une erreur est survenue.",
    loading: "Création en cours…",
    submit: "S’inscrire"
  }
};

export default function SignupForm({ onSuccess, language }: SignupFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const t = TEXTS[language];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register({ username, email, password });
      setLoading(false);
      setSuccess(true);
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 1500);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 bg-white shadow rounded-xl space-y-4">
      <h2 className="text-2xl font-bold text-center">{t.title}</h2>
      <input
        type="text"
        placeholder={t.username}
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
        className="w-full border px-3 py-2 rounded"
      />
      <input
        type="email"
        placeholder={t.email}
        value={email}
        onChange={e => setEmail(e.target.value)}
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
      {success && (
        <div className="text-green-600 mb-4 text-center">
          {t.success}
        </div>
      )}
      {error && <div className="text-red-500">{error}</div>}
      <button
        type="submit"
        disabled={loading || success}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        {loading ? t.loading : t.submit}
      </button>
    </form>
  );
}
