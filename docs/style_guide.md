# 🎨 DataScope_AI – Style Guide (v1.0)

## 1. Palette de couleurs

| Usage           | Couleur principale |
|-----------------|-------------------|
| **Primaire**    | ![#2563eb](https://via.placeholder.com/18/2563eb/000000?text=+) `#2563eb` (blue-600) |
| **Secondaire**  | ![#60a5fa](https://via.placeholder.com/18/60a5fa/000000?text=+) `#60a5fa` (blue-400) |
| **Background**  | ![#f3f4f6](https://via.placeholder.com/18/f3f4f6/000000?text=+) `#f3f4f6` (gray-100), `#ffffff` |
| **Accent**      | ![#6366f1](https://via.placeholder.com/18/6366f1/000000?text=+) `#6366f1` (indigo-500) |
| **Success**     | ![#22c55e](https://via.placeholder.com/18/22c55e/000000?text=+) `#22c55e` (green-500) |
| **Error**       | ![#ef4444](https://via.placeholder.com/18/ef4444/000000?text=+) `#ef4444` (red-500) |

### Palette étendue (à utiliser au besoin – basée sur Tailwind)
- Bleu foncé : `#1e3a8a` (blue-800)
- Indigo foncé : `#3730a3` (indigo-800)
- Gris clair : `#e5e7eb` (gray-200)

---

## 2. Polices de caractères

- **Font principale (texte + titres)** : [DM Sans](https://fonts.google.com/specimen/DM+Sans)
    - `font-family: 'DM Sans', sans-serif;`
- **Alternative** (pour titres si tu veux un léger contraste) : [Inter](https://fonts.google.com/specimen/Inter)
    - `font-family: 'Inter', sans-serif;`
- **Où trouver ?**  
  → Import Google Fonts conseillé dans `index.html` ou via npm/yarn avec Tailwind config

---

## 3. Moodboard & inspiration

- **Type d’interface** : SaaS journalistique, MVP sobre, sérieux, professionnel
- **Mots-clés** : Journalistique, SaaS, neutre, minimal, lisible
- **Références UI** :
    - Notion (pour la clarté et la neutralité)
    - Readwise Reader (interface “tool”, pas “magazine”)
    - Craft Docs (simplicité, neutralité, peu d’effets)
    - Medium (version minimaliste, pas le blog coloré)
- **À éviter** : excès d’illustrations, couleurs criardes, effets “fun” type dashboard analytics
- **Focaliser sur** : 
    - Lisibilité (grandes marges, font taille confortable)
    - Navigation claire et discrète (barre, menus)
    - Zones de contenu bien séparées (cards, sections)

---

## 4. Exemples d’utilisation

- **Boutons** : fond bleu primaire, texte blanc, arrondis moyens
- **Cards et blocs** : fond blanc, bords gris clair, shadow doux, titres bleu primaire
- **Erreurs & succès** : bannières discrètes en vert ou rouge, texte clair

---

## 5. À intégrer

- Ajouter la palette au `tailwind.config.js` (section theme > extend > colors)
- Importer DM Sans dans le projet (`index.html` ou config Tailwind)
- Utiliser ces couleurs et polices pour tous les composants/pages
- Toujours valider lisibilité et contraste (accessibilité !)

---

*Ce style-guide doit être appliqué à toutes les futures features et pages DataScope_AI pour garantir une cohérence visuelle et une image professionnelle.*

