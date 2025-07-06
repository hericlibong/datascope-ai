import SignupForm from '../components/Auth/SignupForm';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';

export default function SignupPage() {
  const navigate = useNavigate();
  const { language } = useLanguage();

  return (
    <SignupForm 
      onSuccess={() => navigate('/login')} 
      language={language} // Passe la langue au composant SignupForm
    />
  );
}
