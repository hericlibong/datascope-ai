// src/components/Layout.tsx
import type { ReactNode } from "react";
import NavbarModern from "@/components/NavbarModern";
import FooterModern from "@/components/FooterModern";

type LayoutProps = { children: ReactNode };

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col font-sans bg-slate-950 text-white">
      <NavbarModern />
      <main className="flex-1">{children}</main>
      <FooterModern />
    </div>
  );
}

