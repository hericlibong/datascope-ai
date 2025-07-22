import { getUsername, clearTokens } from "@/api/auth";
import { Link, useNavigate } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

const LANGS = {
  en: {
    about: "About",
    signin: "Sign in",
    analyze: "New analysis",
    history: "My history",
    logout: "Logout",
    flag: "🇬🇧",
    switch: "fr"
  },
  fr: {
    about: "À propos",
    signin: "Connexion",
    analyze: "Nouvelle analyse",
    history: "Mon historique",
    logout: "Déconnexion",
    flag: "🇫🇷",
    switch: "en"
  }
};

// ...
export default function MainMenu() {
  const username = getUsername();
  const navigate = useNavigate();
  const { language, setLanguage } = useLanguage();
  const t = LANGS[language as "en" | "fr"];

  function switchLanguage() {
    setLanguage(language === "en" ? "fr" : "en");
  }

  function handleLogout() {
    clearTokens();
    navigate("/login");
  }

  return (
    <nav className="flex flex-wrap gap-4 justify-center items-center mb-2">
      {/* NON connecté : About | Switch langue | Sign in */}
      {!username && (
        <>
          <Link to="/about" className="text-blue-600 hover:underline">{t.about}</Link>
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
            {language === "fr" ? "Connexion" : "Sign in"}
          </Link>
        </>
      )}

      {/* CONNECTÉ : menu utilisateur (plus de switch langue) */}
      {username && (
        <>
          <Link to="/about" className="text-blue-600 hover:underline">{t.about}</Link>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 px-3 py-1 rounded bg-white border border-gray-200 hover:bg-gray-50 focus:outline-none">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>{username.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <span className="font-semibold text-gray-700 max-w-[120px] truncate">{username}</span>
                <svg width="16" height="16" fill="none" viewBox="0 0 20 20"><path d="M5 8l5 5 5-5" stroke="#888" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuLabel>
                <div className="flex flex-col">
                  <span className="font-medium">{username}</span>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/analyze">{t.analyze}</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/history">{t.history}</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600 cursor-pointer">
                {t.logout}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </>
      )}
    </nav>
  );
}

