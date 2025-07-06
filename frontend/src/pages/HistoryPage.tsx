import { useEffect, useState } from "react";
import { getUserHistory } from "@/api/history";
import { Link } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  // Texts for both languages
  const texts = {
    fr: {
      title: "Mon historique d’analyses",
      loading: "Chargement…",
      error: "Une erreur est survenue",
      empty: "Aucune analyse enregistrée pour l’instant.",
      unknownDate: "Date inconnue",
      score: "Score :",
      detail: "Voir le détail",
    },
    en: {
      title: "My analysis history",
      loading: "Loading…",
      error: "An error occurred",
      empty: "No saved analysis yet.",
      unknownDate: "Unknown date",
      score: "Score:",
      detail: "See details",
    },
  };

  const t = texts[language] || texts.fr;

  useEffect(() => {
    getUserHistory()
      .then((data) => setHistory(data.results))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">{t.title}</h2>
      {loading && <div>{t.loading}</div>}
      {error && <div className="text-red-600">{t.error}: {error}</div>}
      {!loading && !error && history.length === 0 && (
        <div>{t.empty}</div>
      )}
      <ul className="space-y-3">
        {history.map((a) => (
          <li
            key={a.id}
            className="bg-gray-50 p-4 rounded shadow flex flex-col md:flex-row md:items-center gap-2"
          >
            <div>
              <span className="font-bold">#{a.id}</span> –{" "}
              <span className="italic text-gray-700">
                {a.created_at ? new Date(a.created_at).toLocaleString(language) : t.unknownDate}
              </span>
              {a.score && (
                <span className="ml-4">
                  {t.score} <span className="font-semibold">{a.score}</span>
                </span>
              )}
            </div>
            <Link
              to={`/analyze/${a.id}`}
              className="ml-auto text-blue-600 hover:underline"
            >
              {t.detail}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
