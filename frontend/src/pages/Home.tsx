import { Button } from "@/components/ui/button";
import { Link, useNavigate } from "react-router-dom";
import { getUsername, clearTokens } from "@/api/auth";

export default function Home() {
  const username = getUsername();
  const navigate = useNavigate();

  // Fonction de déconnexion propre
  const handleLogout = () => {
    clearTokens();
    navigate("/login"); // Redirige vers la page de connexion
  };

  return (
    <div className="w-full text-center space-y-6 mt-10">
      {username && (
        <div className="mb-2 flex flex-col items-center">
          <div className="text-green-700 font-bold">
            Connecté en tant que <span className="underline">{username}</span>
          </div>
          <Button
            onClick={handleLogout}
            className="mt-2 bg-red-600 hover:bg-red-700"
            variant="secondary"
          >
            Déconnexion
          </Button>
        </div>
      )}
      <h2 className="text-2xl font-bold">Analyse ton article avec DataScope</h2>
      
      {/* lien vers le signup */}
      <Link to="/signup"> 
        <Button className="mt-4">Créer un compte</Button>
      </Link>

      {/* Bouton vers l’analyse */}
      <Link to="/analyze">
        <Button className="mt-4">Commencer une analyse</Button>
      </Link>

      {/* Lien texte vers la page "À propos" */}
      <div className="mt-6">
        <Link to="/about" className="text-sm text-blue-600 hover:underline">
          En savoir plus sur DataScope →
        </Link>
      </div>
    </div>
  );
}
