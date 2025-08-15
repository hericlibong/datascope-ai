export default function FooterModern() {
const year = new Date().getFullYear();
return (
<footer className="mt-8 w-full border-t border-white/10 bg-slate-950/60 text-slate-300">
<div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-3">
<p className="text-sm">© {year} Datascope — MVP journalist SaaS</p>
<nav className="flex items-center gap-4 text-xs">
<a href="#privacy" className="hover:text-white">Privacy</a>
<a href="#terms" className="hover:text-white">Terms</a>
<a href="#contact" className="hover:text-white">Contact</a>
</nav>
</div>
</footer>
);
}