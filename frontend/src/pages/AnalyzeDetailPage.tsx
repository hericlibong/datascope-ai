import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { authFetch } from "@/api/auth";

export default function AnalyzeDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    authFetch(`http://localhost:8000/api/analysis/${id}/`)
      .then((res) =>
        res.ok
          ? res.json()
          : res.json().then((err: any) => Promise.reject(err.detail || "Erreur"))
      )
      .then(setData)
      .catch((err) => setError(typeof err === "string" ? err : "Erreur"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-center mt-10">Chargement…</div>;
  if (error) return <div className="text-center mt-10 text-red-600">{error}</div>;
  if (!data) return null;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-xl font-bold mb-4">
        Détail de l’analyse #{id}
      </h2>
      <pre className="bg-gray-100 p-4 rounded">{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
