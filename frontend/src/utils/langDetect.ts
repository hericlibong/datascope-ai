// frontend/src/utils/langDetect.ts
import { franc } from "franc-min";

export function detectLang(text: string): "en" | "fr" | "latin" | "other" {
  const cleanText = text.trim().toLowerCase();

  // Détection explicite de "Lorem ipsum"
  if (cleanText.includes("lorem ipsum")) return "latin";

  if (!text || text.length < 20) {
    return "other"; // Trop court pour être fiable
  }

  const code = franc(text);

  if (code === "fra") return "fr";
  if (code === "eng") return "en";
  if (code === "lat") return "latin";

  return "other";
}

