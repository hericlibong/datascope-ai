import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Home() {
  const { language } = useLanguage();

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-8">
      <div className="max-w-2xl space-y-6">
        <h2 className="text-4xl font-bold text-foreground">
          {language === "fr"
            ? "Analyse ton article avec DataScope"
            : "Analyze your article with DataScope"}
        </h2>
        <p className="text-lg text-muted-foreground">
          {language === "fr"
            ? "Découvrez les insights cachés dans vos contenus grâce à l'intelligence artificielle."
            : "Discover hidden insights in your content with artificial intelligence."}
        </p>
      </div>
      <Link to="/login">
        <Button size="lg" className="text-lg px-8 py-3">
          {language === "fr" ? "Commencer une analyse" : "Start an analysis"}
        </Button>
      </Link>
    </div>
  );
}
