import { useLanguage } from "@/contexts/LanguageContext";

export default function About() {
  const { language } = useLanguage();

  return (
    <h2 className="text-2xl font-bold">
      {language === "fr" ? "À propos de DataScope" : "About DataScope"}
    </h2>
  );
}
