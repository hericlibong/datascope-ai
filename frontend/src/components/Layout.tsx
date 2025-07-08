// src/components/Layout.tsx

import { Link } from "react-router-dom"; // Ajoute cet import si ce n'est pas déjà fait
import type { ReactNode } from "react";
import MainMenu from "@/components/Auth/MainMenu";

type LayoutProps = {
  children: ReactNode;
};

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 font-sans">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full bg-white shadow-sm border-b border-gray-200 h-16 flex items-center px-8">
        <Link to="/" className="flex items-center gap-3 flex-1 hover:opacity-90 transition">
          {/* Logo (optionnel, tu peux mettre un SVG ici plus tard) */}
          <span className="inline-block bg-blue-600 rounded-full w-8 h-8 flex items-center justify-center mr-2">
            <span className="text-white text-xl font-bold">D</span>
          </span>
          <span className="text-2xl font-extrabold text-blue-700 tracking-tight select-none">
            DataScope_AI
          </span>
        </Link>
        <MainMenu />
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="w-full bg-white shadow py-2 px-6 mt-4 text-sm text-gray-500 text-center border-t">
        © 2025 DataScope — MVP journalist SaaS
      </footer>
    </div>
  );
}
