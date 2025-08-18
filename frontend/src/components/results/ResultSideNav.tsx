import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface ResultSideNavProps {
  sections: { id: string; label: string }[];
}

export default function ResultSideNav({ sections }: ResultSideNavProps) {
  const [activeId, setActiveId] = useState<string>("");

  // Observer pour highlight section visible
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.find((entry) => entry.isIntersecting);
        if (visible) setActiveId(visible.target.id);
      },
      { threshold: 0.3 }
    );

    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [sections]);

  return (
    <nav className="sticky top-20 p-4 space-y-2 text-sm">
      {sections.map((s) => (
        <a
          key={s.id}
          href={`#${s.id}`}
          className={cn(
            "block px-2 py-1 rounded transition",
            activeId === s.id ? "bg-indigo-600 text-white" : "text-gray-300 hover:text-white"
          )}
        >
          {s.label}
        </a>
      ))}
    </nav>
  );
}
