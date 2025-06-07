// src/components/Layout.tsx

import type { ReactNode } from "react";

type LayoutProps = {
  children: ReactNode;
};

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="w-full bg-white shadow py-4 px-6 mb-4">
        <h1 className="text-xl font-bold text-blue-800">DataScope</h1>
      </header>
      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-center px-6">
        {children}
      </main>
      {/* Footer (optionnel) */}
      <footer className="w-full bg-white shadow py-2 px-6 mt-4 text-sm text-gray-500 text-center">
        © 2025 DataScope
      </footer>
    </div>
  );
}
