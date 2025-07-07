// src/components/Layout.tsx

import type { ReactNode } from "react";
import MainMenu from "@/components/Auth/MainMenu";

type LayoutProps = {
  children: ReactNode;
};

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="w-full bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-foreground">DataScope</h1>
          </div>
          
          {/* Navigation & User Menu */}
          <MainMenu />
        </div>
      </header>
      
      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        {children}
      </main>
      
      {/* Footer - minimal */}
      <footer className="border-t border-border bg-muted/30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-sm text-muted-foreground text-center">
            © 2025 DataScope
          </p>
        </div>
      </footer>
    </div>
  );
}
