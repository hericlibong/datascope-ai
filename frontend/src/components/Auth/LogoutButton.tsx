import { clearTokens } from "@/api/auth";

export default function LogoutButton() {
  const handleLogout = () => {
    clearTokens();
    window.location.href = '/login';
  };

  return (
    <button onClick={handleLogout} className="text-red-600 hover:underline">
      Déconnexion
    </button>
  );
}

