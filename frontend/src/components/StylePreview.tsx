// src/components/StylePreview.tsx
export default function StylePreview() {
    return (
      <div style={{ fontFamily: "'DM Sans', sans-serif", padding: 32, background: "#f3f4f6", minHeight: "100vh" }}>
        <h1 style={{ color: "#2563eb", fontSize: 36, marginBottom: 16 }}>DataScope_AI – Style Guide Preview</h1>
        <p style={{ color: "#1e3a8a" }}>Font: DM Sans (titres & textes)</p>
  
        <div style={{ margin: "32px 0", display: "flex", gap: 16 }}>
          <div style={{ background: "#2563eb", color: "white", padding: "16px 24px", borderRadius: 8 }}>Bouton principal</div>
          <div style={{ background: "#60a5fa", color: "#1e3a8a", padding: "16px 24px", borderRadius: 8 }}>Bouton secondaire</div>
          <div style={{ background: "#6366f1", color: "white", padding: "16px 24px", borderRadius: 8 }}>Accent</div>
        </div>
  
        <div style={{ display: "flex", gap: 32 }}>
          <div style={{ background: "#fff", boxShadow: "0 2px 8px #e5e7eb", borderRadius: 12, padding: 24, width: 260 }}>
            <h2 style={{ color: "#2563eb" }}>Card</h2>
            <p style={{ color: "#4b5563" }}>Texte descriptif de la card, pour voir la couleur de fond et le style.</p>
          </div>
          <div>
            <div style={{ background: "#22c55e", color: "white", borderRadius: 6, padding: "8px 16px", marginBottom: 8 }}>Success (vert)</div>
            <div style={{ background: "#ef4444", color: "white", borderRadius: 6, padding: "8px 16px" }}>Error (rouge)</div>
          </div>
        </div>
  
        <div style={{ marginTop: 40, color: "#6366f1" }}>
          <em>Mood: SaaS journalistique • MVP sobre • Focus sur la lisibilité</em>
        </div>
      </div>
    );
  }
  