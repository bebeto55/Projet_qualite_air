import importlib
import subprocess
import sys

libraries = {
    "supabase": "supabase",
    "sweetviz": "sweetviz",
    "streamlit":"streamlit"
}

for module, package in libraries.items():
    try:
        importlib.import_module(module)
        print(f"[OK] {package} est déjà installé.")
    except ImportError:
        print(f"[INSTALL] Installation de {package}...")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            package
        ])

print("\nToutes les bibliothèques pour la BD sont disponibles !")


