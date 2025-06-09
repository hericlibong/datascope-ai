import { useState, useId } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";

/* ---------------------------------------------------------
   Appel backend : envoie texte / fichier + langue + token
--------------------------------------------------------- */
async function sendAnalysisRequest(
  text: string,
  file: File | null,
  language: "en" | "fr"
) {
  const formData = new FormData();
  if (text) formData.append("text", text);
  if (file) formData.append("file", file);
  formData.append("language", language);

  const token = localStorage.getItem("access_token"); // ← JWT si présent

  const response = await fetch("/api/analysis/", {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: formData,
  });

  if (!response.ok) {
    const { detail } = await response.json().catch(() => ({}));
    throw new Error(detail ?? `Erreur API : ${response.status}`);
  }
  return response.json();
}

/* ---------------------------------------------------------
   Composant principal
--------------------------------------------------------- */
export function AnalysisForm() {
  /* champs */
  const [articleText, setArticleText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<"en" | "fr">("en");

  /* exécution */
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);
  const [result, setResult]     = useState<any>(null);

  const langSwitchId = useId();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await sendAnalysisRequest(articleText, file, language);
      setResult(data);
    } catch (err: any) {
      setError(err.message ?? "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  };

  /* ----------------------------------------------------- */
  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-lg mx-auto">
      {/* langue */}
      <div className="flex items-center gap-4">
        <Label htmlFor={langSwitchId}>Langue d’analyse</Label>
        <span role="img" aria-label="anglais">🇬🇧</span>
        <Switch
          id={langSwitchId}
          checked={language === "fr"}
          onCheckedChange={(v) => setLanguage(v ? "fr" : "en")}
        />
        <span role="img" aria-label="français">🇫🇷</span>
        <span className="text-xs text-gray-500 ml-2">
          {language === "en" ? "English" : "Français"}
        </span>
      </div>

      {/* texte */}
      <div>
        <Label htmlFor="article-text">Texte de l’article</Label>
        <Textarea
          id="article-text"
          rows={8}
          placeholder="Collez ou saisissez votre texte…"
          value={articleText}
          onChange={(e) => setArticleText(e.target.value)}
        />
      </div>

      {/* fichier */}
      <div>
        <Label htmlFor="article-file">Ou téléversez un fichier (.txt)</Label>
        <Input
          id="article-file"
          type="file"
          accept=".txt"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {/* bouton */}
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? "Analyse en cours…" : "Analyser"}
      </Button>

      {/* messages */}
      {error  && <p className="text-red-600">{error}</p>}
      {result && (
        <pre className="mt-4 p-4 bg-gray-100 rounded text-xs whitespace-pre-wrap">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </form>
  );
}
