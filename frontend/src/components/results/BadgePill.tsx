import type { ReactNode } from "react";

export default function BadgePill({
  children, className = "",
}: { children: ReactNode; className?: string }) {
  return (
    <span
      className={
        "inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs md:text-sm " +
        "backdrop-blur-sm " + className
      }
    >
      {children}
    </span>
  );
}
