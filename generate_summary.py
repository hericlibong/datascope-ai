import os
import re

# Répertoires et fichiers à ignorer
EXCLUDE_DIRS = {'venv', '__pycache__', 'node_modules', '.git', 'migrations'}
OUTPUT_FILE = "project_summary.md"

def generate_project_tree(root_dir="."):
    """Génère l'arborescence du projet en texte brut."""
    tree_lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignorer certains dossiers
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        # Calculer l'indentation
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        subdir = os.path.basename(dirpath) if dirpath != "." else root_dir
        tree_lines.append(f"{indent}- {subdir}/")

        # Lister les fichiers
        for filename in filenames:
            if filename.endswith((".py", ".js", ".jsx")):  # On ne garde que le code pertinent
                tree_lines.append(f"{indent}    - {filename}")
    return "\n".join(tree_lines)

def extract_dependencies(root_dir="."):
    """Analyse les fichiers Python et liste les imports principaux."""
    dependency_map = {}
    import_regex = re.compile(r'^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))', re.MULTILINE)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        imports = [m[0] or m[1] for m in import_regex.findall(content)]
                        if imports:
                            dependency_map[filepath] = sorted(set(imports))
                except (UnicodeDecodeError, FileNotFoundError):
                    continue
    return dependency_map

def write_summary(tree_str, dependencies):
    """Écrit la carte du projet et le résumé des dépendances dans un fichier markdown."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Carte du projet Datascope_AI\n\n")
        f.write("## Arborescence\n")
        f.write("```\n")
        f.write(tree_str)
        f.write("\n```\n\n")
        
        f.write("## Dépendances principales\n")
        for file, imports in dependencies.items():
            f.write(f"- **{file}** : {', '.join(imports)}\n")

if __name__ == "__main__":
    tree_str = generate_project_tree(".")
    dependencies = extract_dependencies(".")
    write_summary(tree_str, dependencies)
    print(f"Résumé généré dans {OUTPUT_FILE}")
