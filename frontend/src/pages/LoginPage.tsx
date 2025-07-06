import LoginForm from '../components/Auth/LoginForm';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from "@/contexts/LanguageContext"; // Ajout de l'import

export default function LoginPage() {
  const navigate = useNavigate();
  const { language } = useLanguage(); // Récupération du contexte de langue

  const handleSuccess = () => {
    // Ici on peut rediriger directement car les tokens sont déjà stockés par login()
    navigate('/');
  };

  return (
    <LoginForm onSuccess={handleSuccess} language={language} /> // Passage de la langue au composant LoginForm
  );
}