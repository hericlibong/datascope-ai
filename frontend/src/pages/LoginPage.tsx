import LoginForm from '../components/Auth/LoginForm';

export default function LoginPage() {
  // Pour l’instant, on n’utilise pas encore le token mais on peut l’afficher/logguer
  const handleSuccess = (tokens: any) => {
    // À compléter plus tard : stockage du token et redirection
    console.log('Connexion réussie, tokens JWT :', tokens);
    // Redirection/stockage du token viendra dans l’étape suivante
  };

  return (
    <LoginForm onSuccess={handleSuccess} />
  );
}
