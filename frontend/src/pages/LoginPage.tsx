import LoginForm from '../components/Auth/LoginForm';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    // Ici on peut rediriger directement car les tokens sont déjà stockés par login()
    navigate('/');
  };

  return (
    <LoginForm onSuccess={handleSuccess} />
  );
}
