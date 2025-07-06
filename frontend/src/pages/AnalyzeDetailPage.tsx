import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { authFetch } from "@/api/auth";
import { useLanguage } from "@/contexts/LanguageContext"; // Ajout du contexte de langue

export default function AnalyzeDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage(); // Utilisation du contexte de langue

  useEffect(() => {
    if (!id) return;
    authFetch(`http://localhost:8000/api/analysis/${id}/`)
      .then((res) =>
        res.ok
          ? res.json()
          : res.json().then((err: any) => Promise.reject(err.detail || (language === "fr" ? "Erreur" : "Error")))
      )
      .then(setData)
      .catch((err) => setError(typeof err === "string" ? err : (language === "fr" ? "Erreur" : "Error")))
      .finally(() => setLoading(false));
  }, [id, language]);

  if (loading) return <div className="text-center mt-10">{language === "fr" ? "Chargement…" : "Loading…"}</div>;
  if (error) return <div className="text-center mt-10 text-red-600">{error}</div>;
  if (!data) return null;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-xl font-bold mb-4">
        {language === "fr" ? "Détail de l’analyse" : "Analysis details"} #{id}
      </h2>
      <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
