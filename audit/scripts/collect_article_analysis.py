# scripts/collect_article_analysis.py
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/playground"

def create_article(file_path: str, title: str, lang: str = "fr") -> dict:
    """Crée un article via l'API playground"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    payload = {"title": title, "content": content, "language": lang}
    resp = requests.post(f"{BASE_URL}/articles/?debug=1", json=payload)
    resp.raise_for_status()
    return resp.json()

def create_analysis(article_id: int) -> dict:
    """Lance l'analyse pour un article"""
    payload = {"article": article_id, "profile_label": "playground"}
    resp = requests.post(f"{BASE_URL}/analysis/?debug=1", json=payload)
    resp.raise_for_status()
    return resp.json()

def save_json(data: dict, out_path: str):
    """Enregistre un JSON formaté"""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/collect_article_analysis.py <file.txt> <title> [lang=fr]")
        sys.exit(1)

    file_path = sys.argv[1]
    title = sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) >= 4 else "fr"

    print(f"[+] Création de l’article depuis {file_path} (lang={lang})")
    article = create_article(file_path, title, lang=lang)
    article_id = article["id"]
    save_json(article, f"audit/outputs/article_{article_id}.json")
    print(f"    Article #{article_id} créé et sauvegardé.")

    print(f"[+] Lancement de l’analyse pour l’article {article_id}")
    analysis = create_analysis(article_id)
    analysis_id = analysis["id"]
    save_json(analysis, f"audit/outputs/analysis_{analysis_id}_article_{article_id}.json")
    print(f"    Analyse #{analysis_id} sauvegardée.")
