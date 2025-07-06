import { createContext, useContext, useState, useEffect } from "react";

type Lang = "en" | "fr";
type LangContextType = {
  language: Lang;
  setLanguage: (lang: Lang) => void;
};

const LanguageContext = createContext<LangContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Lang>("en");

  // Persiste la langue dans le localStorage
  useEffect(() => {
    const lang = (localStorage.getItem("lang") as Lang) || "en";
    setLanguage(lang);
  }, []);

  const updateLanguage = (lang: Lang) => {
    setLanguage(lang);
    localStorage.setItem("lang", lang);
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage: updateLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
