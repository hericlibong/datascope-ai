// src/pages/Home.tsx
import { useState } from "react";
import { Link } from "react-router-dom";
import { useLanguage } from "@/contexts/LanguageContext";
import { getUsername } from "@/api/auth";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import SignupForm from "@/components/Auth/SignupForm";
import HeroModern from "@/components/HeroModern";

export default function Home() {
  const { language } = useLanguage();
  const username = getUsername();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Hero présentational — déclenche la modal via onOpenSignup */}
      <HeroModern
        isFr={language === "fr"}
        username={username}
        onOpenSignup={() => setOpen(true)}
      />

      {/* Modal d’inscription contrôlée ici (aucun DialogTrigger nécessaire) */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg mx-auto bg-slate-900 text-white border-white/10">
          <SignupForm
            onSuccess={() => {
              setOpen(false);
            }}
            language={language}
          />
          <div className="mt-4 text-center text-slate-400">
            {language === "fr" ? "Déjà inscrit ? " : "Already registered? "}
            <Link
              to="/login"
              className="text-indigo-300 hover:underline font-semibold"
              onClick={() => setOpen(false)}
            >
              {language === "fr" ? "Connexion" : "Sign in"}
            </Link>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
