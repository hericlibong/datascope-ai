// src/components/HeroModern.tsx
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

type HeroModernProps = {
  isFr: boolean;
  username?: string | null;
  onOpenSignup: () => void; // ouvre la modal d'inscription côté Home
};

/**
 * HeroModern — présentational only (aucune logique d'auth ou de modal ici).
 * - Fond sombre + dégradés + grille subtile
 * - Titre avec accent en gradient
 * - CTAs stylés (Get started => onOpenSignup)
 */
export default function HeroModern({ isFr, username, onOpenSignup }: HeroModernProps) {
  return (
    <section className="relative w-full min-h-[70vh] overflow-hidden bg-slate-950 text-white flex items-center">
      {/* Dégradés de fond */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 [background:radial-gradient(1000px_500px_at_10%_-20%,rgba(59,130,246,0.20),transparent_60%),radial-gradient(700px_350px_at_90%_0%,rgba(236,72,153,0.16),transparent_60%),radial-gradient(500px_300px_at_50%_120%,rgba(251,146,60,0.18),transparent_60%)]"
      />
      {/* Grille subtile */}
      <svg aria-hidden className="absolute inset-0 h-full w-full opacity-[0.12] mix-blend-overlay">
        <defs>
          <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="currentColor" strokeWidth="0.7" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" className="text-slate-400" />
      </svg>

      {/* Contenu */}
      <div className="relative z-10 w-full px-4 py-16">
        <div className="mx-auto max-w-3xl text-center space-y-6">
          {!username ? (
            <>
              <motion.h1
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-4xl sm:text-5xl md:text-6xl font-extrabold leading-tight tracking-tight"
              >
                {isFr ? "Transformez votre rédaction avec " : "Transform your newsroom with "}
                <span className="bg-gradient-to-r from-orange-400 via-fuchsia-500 to-indigo-500 bg-clip-text text-transparent">
                  {isFr ? "la puissance de l’IA" : "the power of AI"}
                </span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05, duration: 0.5 }}
                className="text-lg text-slate-300"
              >
                {isFr
                  ? "Analyse et enrichis tes articles grâce à l’intelligence artificielle et à la data visualisation. Découvre de nouveaux angles et sources en un clic."
                  : "Analyze and enrich your articles with AI and dataviz. Discover new editorial angles and sources in one click."}
              </motion.p>

              <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
                <Button
                  size="lg"
                  onClick={onOpenSignup}
                  className="rounded-2xl bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-orange-400 text-white shadow-xl shadow-fuchsia-500/25 hover:translate-y-[-1px] hover:shadow-2xl transition-all"
                >
                  {isFr ? "Commencer" : "Get Started"}
                </Button>

                <Link
                  to="/login"
                  className="rounded-2xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold text-white backdrop-blur hover:bg-white/10"
                >
                  {isFr ? "Se connecter" : "Sign in"}
                </Link>
              </div>

              {/* Logos confiance (facultatif) */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.15, duration: 0.5 }}
                className="mx-auto mt-10 max-w-4xl"
              >
                <p className="text-xs uppercase tracking-widest text-slate-400">
                  {isFr ? "Déjà utilisé par des équipes médias" : "Already trusted by media teams"}
                </p>
                <div className="mt-3 grid grid-cols-2 items-center gap-4 opacity-80 sm:grid-cols-3 md:grid-cols-6">
                  {["Lavender", "Writesonic", "10Web", "Typewise", "Newsroom.AI", "Wisedesk"].map((b) => (
                    <div
                      key={b}
                      className="flex h-10 items-center justify-center rounded-lg border border-white/5 bg-white/5 px-2 text-xs text-slate-300"
                    >
                      {b}
                    </div>
                  ))}
                </div>
              </motion.div>
            </>
          ) : (
            <>
              <motion.h2
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-3xl sm:text-4xl font-bold"
              >
                {isFr ? `Bienvenue, ${username} !` : `Welcome, ${username}!`}
              </motion.h2>

              <p className="text-slate-300">
                {isFr ? "Prêt à analyser un nouvel article ?" : "Ready to analyze a new article?"}
              </p>

              <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
                <Link to="/analyze">
                  <Button className="rounded-2xl bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-orange-400 text-white hover:opacity-95" size="lg">
                    {isFr ? "Nouvelle analyse" : "New analysis"}
                  </Button>
                </Link>
                <Link to="/history" className="text-indigo-300 hover:underline">
                  {isFr ? "Voir mon historique" : "See my analysis history"}
                </Link>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Vignette douce */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-white/10 [mask-image:radial-gradient(70%_70%_at_50%_30%,black,transparent)]"
      />
    </section>
  );
}
