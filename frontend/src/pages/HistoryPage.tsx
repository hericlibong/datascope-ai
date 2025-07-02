import { useEffect, useState } from "react";
import { getUserHistory } from "@/api/history";
import { Link } from "react-router-dom";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getUserHistory()
      .then((data) => setHistory(data.results))  // <--- On extrait "results" !
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Mon historique d’analyses</h2>
      {loading && <div>Chargement…</div>}
      {error && <div className="text-red-600">{error}</div>}
      {!loading && !error && history.length === 0 && (
        <div>Aucune analyse enregistrée pour l’instant.</div>
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
                {a.created_at ? new Date(a.created_at).toLocaleString() : "Date inconnue"}
              </span>
              {a.score && (
                <span className="ml-4">
                  Score : <span className="font-semibold">{a.score}</span>
                </span>
              )}
            </div>
            <Link
              to={`/analyze/${a.id}`}
              className="ml-auto text-blue-600 hover:underline"
            >
              Voir le détail
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
