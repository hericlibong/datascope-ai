// src/pages/Home.tsx
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { getUsername } from "@/api/auth";

export default function Home() {
  const { language } = useLanguage();
  const username = getUsername();

  return (
    <section className="w-full flex flex-col items-center justify-center py-16 px-4 bg-gray-50 min-h-[70vh]">
      <div className="max-w-2xl mx-auto text-center space-y-8">
        {!username ? (
          <>
            <h1 className="text-4xl font-extrabold text-blue-700 leading-tight">
              {language === "fr"
                ? "DataScope, l’IA au service du journalisme de données"
                : "DataScope: AI-powered data-journalism"}
            </h1>
            <p className="text-lg text-gray-600">
              {language === "fr"
                ? "Analyse et enrichis tes articles grâce à l’intelligence artificielle et à la data visualisation. Découvre de nouveaux angles et sources en un clic."
                : "Analyze and enrich your articles with AI and dataviz. Discover new editorial angles and sources in one click."}
            </p>
            <Link to="/signup">
              <Button size="lg" className="mt-6 px-8 py-3 text-lg font-semibold">
                {language === "fr" ? "Commencer" : "Get Started"}
              </Button>
            </Link>
            <div className="mt-2 text-gray-500">
              {language === "fr"
                ? "Déjà inscrit ? "
                : "Already registered? "}
              <Link to="/login" className="text-blue-600 hover:underline font-semibold">
                {language === "fr" ? "Connexion" : "Sign in"}
              </Link>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-3xl font-bold text-blue-700">
              {language === "fr"
                ? `Bienvenue, ${username} !`
                : `Welcome, ${username}!`}
            </h2>
            <p className="text-gray-600">
              {language === "fr"
                ? "Prêt à analyser un nouvel article ?"
                : "Ready to analyze a new article?"}
            </p>
            <Link to="/analyze">
              <Button size="lg" className="mt-6 px-8 py-3 text-lg font-semibold bg-indigo-600 hover:bg-indigo-700">
                {language === "fr" ? "Nouvelle analyse" : "New analysis"}
              </Button>
            </Link>
            <div className="mt-3">
              <Link to="/history" className="text-blue-600 hover:underline">
                {language === "fr"
                  ? "Voir mon historique"
                  : "See my analysis history"}
              </Link>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
