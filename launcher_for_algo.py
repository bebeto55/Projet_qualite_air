import importlib
import subprocess
import sys

libraries = {
    "sklearn": "scikit-learn",
    "xgboost": "xgboost",
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

print("\n[DONE] Toutes les bibliothèques sont disponibles.")
