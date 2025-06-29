import SignupForm from '../components/Auth/SignupForm';
import { useNavigate } from 'react-router-dom';

export default function SignupPage() {
  const navigate = useNavigate();

  return (
    <SignupForm onSuccess={() => navigate('/login')} />
  );
}
