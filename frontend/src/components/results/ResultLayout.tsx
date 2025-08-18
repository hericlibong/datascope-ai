import type { ReactNode } from "react";
import ResultSideNav from "./ResultSideNav";

interface ResultLayoutProps {
  sections: { id: string; label: string }[];
  children: ReactNode;
}

export default function ResultLayout({ sections, children }: ResultLayoutProps) {
  return (
    <div className="flex w-full">
      <aside className="hidden md:block w-60 border-r border-white/10 bg-slate-950/80 backdrop-blur-sm">
        <ResultSideNav sections={sections} />
      </aside>
      <main className="flex-1 p-6 space-y-10">{children}</main>
    </div>
  );
}
