import React, { useState } from "react";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import { Rating } from "@smastrom/react-rating";
import "@smastrom/react-rating/style.css";
import { envoyerFeedback } from "@/api/feedback";

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
    try {
      await envoyerFeedback({
        analysis: analysisId,
        relevance,
        angles,
        sources,
        reusability,
        message: message,
      });
      setSuccess(true);
      setMessage(""); // Reset du champ commentaire
      setRelevance(0);
      setAngles(0);
      setSources(0);
      setReusability(0);
      setTimeout(() => setSuccess(false), 3000); // Masquer le message après 3s
    } catch (err: any) {
      setError(err?.message || labels.error);
    } finally {
      setLoading(false);
    }
  };

  if (success)
    return (
      <div className="p-4 bg-green-500/10 border border-green-500/20 rounded text-green-400 text-center">
        {labels.success}
      </div>
    );

  return (
    <Accordion type="single" collapsible className="w-full mt-4">
      <AccordionItem value="feedback" className="border border-white/10 rounded-lg bg-white/5">
        <AccordionTrigger className="px-4 text-white hover:no-underline">
          <span>{labels.title}</span>
        </AccordionTrigger>
        <AccordionContent className="px-4 pb-4">
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
                <Label htmlFor="feedback-comment" className="text-slate-300">{labels.comment}</Label>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="ml-1 cursor-pointer text-slate-400">🛈</span>
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
                className="min-h-[60px] bg-white/5 border-white/20 text-white placeholder:text-slate-400"
              />
            </div>
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded">
                {error}
              </div>
            )}
            <Button 
              type="submit" 
              disabled={loading || !oneSelected([relevance, angles, sources, reusability])}
              className="bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white"
            >
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
      <Label className="min-w-[160px] text-slate-300">{label}</Label>
      <Rating
        value={value}
        onChange={onChange}
        style={{ maxWidth: 110 }}
        isRequired
      />
      {value > 0 && <span className="text-xs text-slate-400">{value}/5</span>}
    </div>
  );
}

// Au moins un critère doit être noté
function oneSelected(values: number[]) {
  return values.some((v) => v > 0);
}
