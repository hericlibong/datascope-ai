import LoginForm from '../components/Auth/LoginForm';
import { useNavigate, useSearchParams  } from 'react-router-dom';
import { useLanguage } from "@/contexts/LanguageContext"; // Ajout de l'import

export default function LoginPage() {
  const navigate = useNavigate();
  const { language } = useLanguage(); // Récupération du contexte de langue
  const [searchParams] = useSearchParams();

  const expired = searchParams.get('expired') === '1';
  const infoMessage = expired
    ? language === 'fr'
      ? 'Votre session a expiré, veuillez vous reconnecter.'
      : 'Your session has expired, please log in again.'
    : null;

  const handleSuccess = () => {
    // Ici on peut rediriger directement car les tokens sont déjà stockés par login()
    navigate('/');
  };

  console.log("params:", searchParams.toString(), "expired:", expired, "infoMessage:", infoMessage);


  return (
    <LoginForm onSuccess={handleSuccess} language={language} message={infoMessage} /> // Passage de la langue au composant LoginForm
  );
}