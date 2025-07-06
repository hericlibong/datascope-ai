// src/components/Layout.tsx

import type { ReactNode } from "react";
import MainMenu from "@/components/Auth/MainMenu";

type LayoutProps = {
  children: ReactNode;
};

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-secondary/30">
      {/* Header */}
      <header className="w-full bg-card shadow py-4 px-6 mb-4 flex flex-col items-center border-b">
        <h1 className="text-xl font-semibold text-primary mb-2">DataScope AI</h1>
        <MainMenu />
      </header>
      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6">
        {children}
      </main>
      {/* Footer */}
      <footer className="w-full bg-card shadow py-2 px-6 mt-4 text-sm text-muted-foreground text-center border-t">
        © 2025 DataScope AI
      </footer>
    </div>
  );
}
