// src/components/Auth/MainMenu.tsx
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
import { cn } from "@/lib/utils";

const LANGS = {
  en: {
    about: "About",
    signin: "Sign in",
    analyze: "New analysis",
    history: "My history",
    logout: "Logout",
    flag: "🇬🇧",
    switch: "fr",
  },
  fr: {
    about: "À propos",
    signin: "Connexion",
    analyze: "Nouvelle analyse",
    history: "Mon historique",
    logout: "Déconnexion",
    flag: "🇫🇷",
    switch: "en",
  },
} as const;

type Variant = "light" | "dark";

type Props = {
  /** Apparence du menu (clair/sombre). Par défaut: "light". */
  variant?: Variant;
  className?: string;
};

export default function MainMenu({ variant = "light", className }: Props) {
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

  const isDark = variant === "dark";
  const linkBase = isDark
    ? "text-slate-200 hover:text-white"
    : "text-blue-600 hover:underline";

  return (
    <nav className={cn("flex flex-wrap gap-4 justify-center items-center", className)}>
      {/* NON connecté : About | Switch langue | Sign in */}
      {!username && (
        <>
          <Link to="/about" className={linkBase}>
            {t.about}
          </Link>

          <button
            onClick={switchLanguage}
            className={cn(
              "ml-2 flex items-center px-2 py-1 rounded border text-sm transition-colors",
              isDark
                ? "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
                : "border-gray-300 bg-white text-gray-800 hover:bg-gray-50"
            )}
            title={language === "en" ? "Passer en français" : "Switch to English"}
            aria-label={language === "en" ? "Passer en français" : "Switch to English"}
          >
            <span className="text-lg mr-1">{t.flag}</span>
            <span className="text-xs">{language === "en" ? "FR" : "EN"}</span>
          </button>

          <Link to="/login" className={cn(linkBase, "font-semibold")}>
            {t.signin}
          </Link>
        </>
      )}

      {/* CONNECTÉ : menu utilisateur */}
      {username && (
        <>
          <Link to="/about" className={linkBase}>
            {t.about}
          </Link>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className={cn(
                  "flex items-center gap-2 px-3 py-1 rounded border focus:outline-none transition-colors",
                  isDark
                    ? "bg-white/5 border-white/10 hover:bg-white/10 text-slate-200"
                    : "bg-white border-gray-200 hover:bg-gray-50 text-gray-700"
                )}
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback>{username.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <span
                  className={cn(
                    "font-semibold max-w-[140px] truncate",
                    isDark ? "text-slate-200" : "text-gray-700"
                  )}
                >
                  {username}
                </span>
                <svg width="16" height="16" fill="none" viewBox="0 0 20 20" aria-hidden="true">
                  <path
                    d="M5 8l5 5 5-5"
                    stroke={isDark ? "#94a3b8" : "#888"}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent
              align="end"
              className={cn("w-48", isDark ? "bg-slate-900 text-slate-100 border-white/10" : undefined)}
            >
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
              <DropdownMenuItem
                onClick={handleLogout}
                className={cn("cursor-pointer", isDark ? "text-red-400" : "text-red-600")}
              >
                {t.logout}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </>
      )}
    </nav>
  );
}
