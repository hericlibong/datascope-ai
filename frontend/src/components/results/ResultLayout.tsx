import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface Section {
  id: string;
  label: string;
  labelFr: string;
}

interface ResultLayoutProps {
  children: React.ReactNode;
  language: "en" | "fr";
}

const sections: Section[] = [
  { id: "overview", label: "Overview", labelFr: "Vue d'ensemble" },
  { id: "angles", label: "Editorial Angles", labelFr: "Angles éditoriaux" },
  { id: "entities", label: "Entities & Themes", labelFr: "Entités & thèmes" },
  { id: "datasets", label: "Datasets", labelFr: "Jeux de données" },
  { id: "feedback", label: "Feedback", labelFr: "Feedback" },
];

export function ResultLayout({ children, language }: ResultLayoutProps) {
  const [activeSection, setActiveSection] = useState("overview");

  useEffect(() => {
    const handleScroll = () => {
      const sectionElements = sections.map(section => 
        document.getElementById(section.id)
      ).filter(Boolean);

      for (const element of sectionElements) {
        if (element) {
          const rect = element.getBoundingClientRect();
          if (rect.top <= 100 && rect.bottom >= 100) {
            setActiveSection(element.id);
            break;
          }
        }
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 relative">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,_rgba(255,255,255,0.05)_1px,_transparent_0)] bg-[size:20px_20px] pointer-events-none" />
      
      <div className="relative flex max-w-7xl mx-auto">
        {/* Sticky SideNav */}
        <nav className="sticky top-20 h-fit w-64 p-6 hidden lg:block">
          <div className="space-y-2">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => scrollToSection(section.id)}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg text-sm transition-all",
                  "hover:bg-white/10 hover:text-white",
                  activeSection === section.id
                    ? "bg-white/10 text-white border-l-2 border-indigo-500"
                    : "text-slate-400"
                )}
              >
                {language === "fr" ? section.labelFr : section.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Main content area */}
        <main className="flex-1 p-6 lg:pl-0">
          {children}
        </main>
      </div>
    </div>
  );
}