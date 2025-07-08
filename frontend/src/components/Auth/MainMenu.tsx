import { getUsername, clearTokens } from "@/api/auth";
import { Link, useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext"; // Ajout du hook

const LANGS = {
  en: {
    home: "Home",
    about: "About",
    signup: "Sign up",
    login: "Login",
    analyze: "New analysis",
    history: "My history",
    logout: "Logout",
    welcome: "Connected as",
    flag: "🇬🇧",
    switch: "fr"
  },
  fr: {
    home: "Accueil",
    about: "À propos",
    signup: "S’enregistrer",
    login: "Connexion",
    analyze: "Nouvelle analyse",
    history: "Mon historique",
    logout: "Déconnexion",
    welcome: "Connecté en tant que",
    flag: "🇫🇷",
    switch: "en"
  }
};

export default function MainMenu() {
  const username = getUsername();
  const navigate = useNavigate();
  const { language, setLanguage } = useLanguage();

  function switchLanguage() {
    setLanguage(language === "en" ? "fr" : "en");
  }

  const t = LANGS[language as "en" | "fr"];

  function handleLogout() {
    clearTokens();
    navigate("/login");
  }

  return (
    <nav className="flex flex-wrap gap-4 justify-center items-center mb-2">
      {/* Version utilisateur NON connecté */}
      {!username && (
        <>
          <Link to="/about" className="text-blue-600 hover:underline">
            {t.about}
          </Link>
          <button
            onClick={switchLanguage}
            className="ml-2 flex items-center px-2 py-1 rounded border border-gray-300 bg-white"
            title={language === "en" ? "Passer en français" : "Switch to English"}
            aria-label={language === "en" ? "Passer en français" : "Switch to English"}
          >
            <span className="text-lg mr-1">{t.flag}</span>
            <span className="text-xs">{language === "en" ? "FR" : "EN"}</span>
          </button>
          <Link to="/login" className="text-blue-600 hover:underline font-semibold">
            {/* On force le label en anglais pour cohérence visuelle */}
            {language === "fr" ? "Sign in" : "Sign in"}
          </Link>
        </>
      )}
      {/* Version utilisateur connecté */}
      {username && (
        <>
          <Link to="/analyze" className="text-blue-600 hover:underline">{t.analyze}</Link>
          <Link to="/history" className="text-blue-600 hover:underline">{t.history}</Link>
          <span className="font-semibold text-green-700 ml-2">({username})</span>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white rounded px-3 py-1 ml-2 hover:bg-red-700"
          >
            {t.logout}
          </button>
        </>
      )}
    </nav>
  );
}