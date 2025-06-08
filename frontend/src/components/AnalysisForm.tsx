import { useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useId } from "react";

// Fonction d'appel à l'API backend
async function sendAnalysisRequest({
  articleText,
  file,
  language,
}: {
  articleText: string;
  file: File | null;
  language: string;
}) {
  const formData = new FormData();
  if (articleText) formData.append("text", articleText);
  if (file) formData.append("file", file);
  formData.append("language", language);

  const response = await fetch("/api/analysis/", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Erreur API : ${response.status}`);
  }
  return response.json();
}

export function AnalysisForm() {
  const [articleText, setArticleText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<"en" | "fr">("en");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const langSwitchId = useId();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiResult = await sendAnalysisRequest({
        articleText,
        file,
        language,
      });
      setResult(apiResult);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l’appel à l’API");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-lg mx-auto">
      {/* Sélecteur de langue */}
      <div className="flex items-center gap-4 mb-2">
        <Label htmlFor={langSwitchId}>Langue d’analyse</Label>
        <div className="flex items-center gap-2">
          <span role="img" aria-label="anglais">🇬🇧</span>
          <Switch
            id={langSwitchId}
            checked={language === "fr"}
            onCheckedChange={v => setLanguage(v ? "fr" : "en")}
          />
          <span role="img" aria-label="français">🇫🇷</span>
        </div>
        <span className="text-xs ml-4 text-gray-500">{language === "en" ? "English" : "Français"}</span>
      </div>

      {/* Zone de texte */}
      <div>
        <Label htmlFor="article-text" className="block mb-1">Texte de l’article</Label>
        <Textarea
          id="article-text"
          placeholder="Collez ou saisissez le texte de votre article à analyser…"
          value={articleText}
          onChange={e => setArticleText(e.target.value)}
          rows={8}
        />
      </div>
      {/* Fichier texte */}
      <div>
        <Label htmlFor="article-file" className="block mb-1">Ou téléversez un fichier (.txt)</Label>
        <Input
          id="article-file"
          type="file"
          accept=".txt"
          onChange={e => setFile(e.target.files?.[0] || null)}
        />
      </div>
      {/* Bouton d’analyse */}
      <Button type="submit" disabled={loading} className="w-full flex items-center justify-center">
        {loading ? (
          <>
            <svg className="animate-spin mr-2 h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            Analyse en cours...
          </>
        ) : (
          "Analyser"
        )}
      </Button>
      {/* Affichage du résultat ou de l’erreur */}
      {error && <div className="text-red-600 mt-2">Erreur : {error}</div>}
      {result && (
        <div className="mt-4 p-4 border rounded bg-green-50 text-green-800">
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </form>
  );
}
