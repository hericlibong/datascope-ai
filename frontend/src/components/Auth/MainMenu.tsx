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
  const { language, setLanguage } = useLanguage(); // Utilisation du contexte

  function switchLanguage() {
    setLanguage(language === "en" ? "fr" : "en");
  }

  const t = LANGS[language as "en" | "fr"];

  function handleLogout() {
    clearTokens();
    navigate("/login");
  }

  return (
    <nav className="flex items-center gap-6">
      {/* Main navigation */}
      <div className="flex items-center gap-4">
        <Link 
          to="/" 
          className="text-foreground hover:text-primary transition-colors font-medium"
        >
          {t.home}
        </Link>
        {username && (
          <>
            <Link 
              to="/analyze" 
              className="text-foreground hover:text-primary transition-colors font-medium"
            >
              {t.analyze}
            </Link>
            <Link 
              to="/history" 
              className="text-foreground hover:text-primary transition-colors font-medium"
            >
              {t.history}
            </Link>
          </>
        )}
        {!username && (
          <Link 
            to="/about" 
            className="text-foreground hover:text-primary transition-colors font-medium"
          >
            {t.about}
          </Link>
        )}
      </div>

      {/* User actions */}
      <div className="flex items-center gap-3 border-l border-border pl-6">
        {/* Language switcher */}
        <button
          onClick={switchLanguage}
          className="flex items-center px-2 py-1 rounded border border-border bg-background hover:bg-accent transition-colors"
          title={language === "en" ? "Passer en français" : "Switch to English"}
          aria-label={language === "en" ? "Passer en français" : "Switch to English"}
        >
          <span className="text-sm mr-1">{t.flag}</span>
          <span className="text-xs">{language === "en" ? "FR" : "EN"}</span>
        </button>

        {!username && (
          <>
            <Link 
              to="/login" 
              className="text-foreground hover:text-primary transition-colors font-medium"
            >
              {t.login}
            </Link>
            <Link 
              to="/signup" 
              className="bg-primary text-primary-foreground hover:bg-primary/90 px-3 py-2 rounded-md transition-colors font-medium"
            >
              {t.signup}
            </Link>
          </>
        )}
        
        {username && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground">
              {t.welcome} <span className="font-semibold text-foreground">{username}</span>
            </span>
            <button
              onClick={handleLogout}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90 px-3 py-2 rounded-md transition-colors font-medium text-sm"
            >
              {t.logout}
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}
