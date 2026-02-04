import json
import os
import sys
import joblib

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BG_DIR = os.path.join(BASE_DIR, "lineD_background")
ECDF_PY = os.path.join(BG_DIR, "lineD_ecdf.py")
PKL_PATH = os.path.join(BG_DIR, "ecdf.pkl")
JSON_PATH = os.path.join(BG_DIR, "all_bdg_51_pkl.json")


def ensure_ecdf_py():
    if os.path.exists(ECDF_PY):
        return
    with open(ECDF_PY, "w") as f:
        f.write("import numpy as np\n\n")
        f.write("class DummyECDF:\n")
        f.write("    def __call__(self, x):\n")
        f.write("        x = np.asarray(x)\n")
        f.write("        return np.zeros_like(x, dtype=float)\n")


def main():
    os.makedirs(BG_DIR, exist_ok=True)
    ensure_ecdf_py()
    sys.path.insert(0, BG_DIR)
    from lineD_ecdf import DummyECDF

    joblib.dump(DummyECDF(), PKL_PATH)
    mapping = {str(i): os.path.basename(PKL_PATH) for i in range(51)}
    with open(JSON_PATH, "w") as f:
        json.dump(mapping, f)

    print(os.path.relpath(PKL_PATH))
    print(os.path.relpath(JSON_PATH))


if __name__ == "__main__":
    main()
