import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";

export default function Home() {
  const { language } = useLanguage();

  return (
    <div className="w-full text-center space-y-6 mt-10">
      <h2 className="text-2xl font-bold">
        {language === "fr"
          ? "Analyse ton article avec DataScope"
          : "Analyze your article with DataScope"}
      </h2>
      <Link to="/login">
        <Button className="mt-4">
          {language === "fr" ? "Commencer une analyse" : "Start an analysis"}
        </Button>
      </Link>
    </div>
  );
}
