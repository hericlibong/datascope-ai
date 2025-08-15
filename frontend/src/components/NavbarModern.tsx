import { Link } from "react-router-dom";
import MainMenu from "@/components/Auth/MainMenu";


export default function NavbarModern() {
return (
<header className="sticky top-0 z-50 w-full">
<div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
{/* Fond translucide + blur + bordure */}
<div className="absolute inset-0 -z-10 backdrop-blur supports-[backdrop-filter]:bg-slate-950/50 border-b border-white/10 rounded-b-2xl" />


<div className="flex h-16 items-center justify-between">
{/* Brand */}
<Link to="/" className="group flex items-center gap-3 pr-3">
<div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-[0_0_24px_rgba(99,102,241,0.35)]">
<span className="text-white text-lg font-black leading-none">Δ</span>
</div>
<span className="text-lg font-semibold tracking-tight text-white">
Datascope<span className="text-indigo-400">_AI</span>
</span>
</Link>


{/* Menu utilisateur/langue (réutilise la logique existante) */}
<div className="ml-auto">
<MainMenu variant="dark" />
</div>
</div>
</div>


{/* Ligne/ombre subtile sous la navbar pour séparer le contenu */}
<div className="h-px w-full bg-gradient-to-r from-transparent via-white/10 to-transparent" />
</header>
);
}