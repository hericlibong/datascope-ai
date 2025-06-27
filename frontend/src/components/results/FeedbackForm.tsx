import React, { useState } from "react";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { Rating } from "@smastrom/react-rating";
import "@smastrom/react-rating/style.css";

type FeedbackFormProps = {
  analysisId: number;
  language: "fr" | "en";
};

const FEEDBACK_LABELS = {
  fr: {
    title: "Donner votre avis sur l’analyse",
    pertinence: "Pertinence de l’analyse",
    angles: "Qualité des angles éditoriaux",
    sources: "Pertinence des sources suggérées",
    reusability: "Potentiel de réutilisation",
    comment: "Commentaire (facultatif)",
    commentTip: "Expliquez votre note, signalez une incohérence, ou partagez une remarque.",
    send: "Envoyer",
    success: "Merci pour votre retour !",
    error: "Erreur lors de l'envoi. Réessayez.",
  },
  en: {
    title: "Give your feedback on the analysis",
    pertinence: "Relevance of the analysis",
    angles: "Quality of editorial angles",
    sources: "Relevance of suggested sources",
    reusability: "Reusability potential",
    comment: "Comment (optional)",
    commentTip: "Explain your rating, flag any inconsistency, or leave a suggestion.",
    send: "Send",
    success: "Thank you for your feedback!",
    error: "Error while submitting. Please try again.",
  },
};

export function FeedbackForm({ analysisId, language }: FeedbackFormProps) {
  const [relevance, setRelevance] = useState(0);
  const [angles, setAngles] = useState(0);
  const [sources, setSources] = useState(0);
  const [reusability, setReusability] = useState(0);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const labels = FEEDBACK_LABELS[language];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const token = localStorage.getItem("access_token"); // Récupère le token
    try {
      const res = await fetch("http://localhost:8000/api/feedbacks/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          analysis: analysisId,
          relevance,
          angles,
          sources,
          reusability,
          message,
        }),
      });
      if (!res.ok) throw new Error();
      setSuccess(true);
    } catch {
      setError(labels.error);
    } finally {
      setLoading(false);
    }
  };

  if (success)
    return (
      <div className="p-4 bg-green-50 border border-green-300 rounded text-green-800 text-center">
        {labels.success}
      </div>
    );

  return (
    <Accordion type="single" collapsible className="w-full mt-4">
      <AccordionItem value="feedback">
        <AccordionTrigger>
          <span>{labels.title}</span>
        </AccordionTrigger>
        <AccordionContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Critères d'évaluation */}
            <div className="space-y-3">
              <Criterion
                label={labels.pertinence}
                value={relevance}
                onChange={setRelevance}
              />
              <Criterion
                label={labels.angles}
                value={angles}
                onChange={setAngles}
              />
              <Criterion
                label={labels.sources}
                value={sources}
                onChange={setSources}
              />
              <Criterion
                label={labels.reusability}
                value={reusability}
                onChange={setReusability}
              />
            </div>
            {/* Champ commentaire */}
            <div>
              <div className="flex items-center gap-2">
                <Label htmlFor="feedback-comment">{labels.comment}</Label>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="ml-1 cursor-pointer text-gray-400">🛈</span>
                    </TooltipTrigger>
                    <TooltipContent>
                      <span>{labels.commentTip}</span>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <Textarea
                id="feedback-comment"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={labels.commentTip}
                className="min-h-[60px]"
              />
            </div>
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded">
                {error}
              </div>
            )}
            <Button type="submit" disabled={loading || !oneSelected([relevance, angles, sources, reusability])}>
              {loading ? "..." : labels.send}
            </Button>
          </form>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}

// Composant critère avec étoiles
type CriterionProps = {
  label: string;
  value: number;
  onChange: (v: number) => void;
};
function Criterion({ label, value, onChange }: CriterionProps) {
  return (
    <div className="flex items-center gap-4">
      <Label className="min-w-[160px]">{label}</Label>
      <Rating
        value={value}
        onChange={onChange}
        style={{ maxWidth: 110 }}
        isRequired
      />
      {value > 0 && <span className="text-xs text-gray-500">{value}/5</span>}
    </div>
  );
}

// Au moins un critère doit être noté
function oneSelected(values: number[]) {
  return values.some((v) => v > 0);
}
