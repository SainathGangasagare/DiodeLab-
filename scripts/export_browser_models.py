"""Export the unchanged seven Python model artifacts for static GitHub Pages.

Run from the repository root with: python scripts/export_browser_models.py
The original joblib files and python-app/app.py are read only.
"""
from __future__ import annotations
import json, sys, warnings
from pathlib import Path
import joblib
import numpy as np
import sklearn

REPO = Path(__file__).resolve().parents[1]
PYTHON_APP = REPO / "python-app"
OUT = REPO / "assets" / "browser-models.json"


def inverse_log_current(x):
    return np.power(10.0, x)


def load_compatible(path: Path):
    sys.modules["__main__"].inverse_log_current = inverse_log_current
    # sklearn 1.8+ removed this private compatibility class. The repository's
    # original requirements pin 1.6.1, where the class is already present.
    import sklearn.compose._column_transformer as ct
    if not hasattr(ct, "_RemainderColsList"):
        class _RemainderColsList(list):
            pass
        ct._RemainderColsList = _RemainderColsList
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return joblib.load(path)


def dense(x):
    return x.toarray() if hasattr(x, "toarray") else x


def export_forest(model):
    trees = []
    for est in model.estimators_:
        t = est.tree_
        trees.append({
            "left": t.children_left.astype(int).tolist(),
            "right": t.children_right.astype(int).tolist(),
            "feature": t.feature.astype(int).tolist(),
            "threshold": t.threshold.astype(float).tolist(),
            "value": t.value[:, 0, 0].astype(float).tolist(),
        })
    return {"kind": "randomForest", "nFeatures": int(model.n_features_in_), "trees": trees}


def export_svr(svr, feature_order, scaler=None, categories=None, target_transform="identity"):
    return {
        "kind": "rbfSvr", "featureOrder": feature_order, "scaler": scaler,
        "categories": categories,
        "supportVectors": np.asarray(dense(svr.support_vectors_), dtype=float).tolist(),
        "dualCoefficients": np.asarray(dense(svr.dual_coef_), dtype=float)[0].tolist(),
        "intercept": float(svr.intercept_[0]), "gamma": float(svr._gamma),
        "targetTransform": target_transform,
    }


def export_simple(model):
    scaler, svr = model.named_steps["standardscaler"], model.named_steps["svr"]
    return export_svr(svr, ["v_meas"], {"mean": scaler.mean_.astype(float).tolist(), "scale": scaler.scale_.astype(float).tolist()})


def export_material(model, multi):
    if multi:
        pipe = model.regressor_
        pre = pipe.named_steps["preprocessor"]
        svr = pipe.named_steps["svr"]
        numeric = pre.named_transformers_["numbers"]
        category = pre.named_transformers_["device"]
        order, target = ["voltage_V", "temperature_K", "device"], "pow10"
    else:
        pre = model.named_steps["columntransformer"]
        svr = model.named_steps["svr"]
        numeric = pre.named_transformers_["numeric"]
        category = pre.named_transformers_["device"]
        order, target = ["device", "voltage_V", "temperature_K"], "log10"
    scaler = {"mean": numeric.mean_.astype(float).tolist(), "scale": numeric.scale_.astype(float).tolist()}
    categories = [str(value) for value in category.categories_[0].tolist()]
    return export_svr(svr, order, scaler, categories, target)


def main():
    paths = {
        "Random Forest": "random_forest_model.joblib",
        "Tuned SVR": "tuned_svr_model.joblib",
        "Silicon SVR": "trained_models/silicon_svr.joblib",
        "SiC SVR": "trained_models/silicon_carbide_svr.joblib",
        "Silicon multi-temperature SVR": "trained_models/silicon_multi_temperature_svr.joblib",
        "SiC multi-temperature SVR": "trained_models/silicon_carbide_multi_temperature_svr.joblib",
        "1N4004 Reverse-bias SVR": "1n4004_reverse_svr_model.joblib",
    }
    models = {name: load_compatible(PYTHON_APP / rel) for name, rel in paths.items()}
    payload = {
        "formatVersion": 1,
        "sourceArtifacts": paths,
        "originalSerializedWith": "scikit-learn 1.6.1 (per python-app/docs/ENVIRONMENT_AND_VERSION.md)",
        "exportEnvironment": {"python": sys.version.split()[0], "scikitLearn": sklearn.__version__},
        "models": {
            "Random Forest": export_forest(models["Random Forest"]),
            "Tuned SVR": export_simple(models["Tuned SVR"]),
            "1N4004 Reverse-bias SVR": export_simple(models["1N4004 Reverse-bias SVR"]),
            "Silicon SVR": export_material(models["Silicon SVR"], False),
            "SiC SVR": export_material(models["SiC SVR"], False),
            "Silicon multi-temperature SVR": export_material(models["Silicon multi-temperature SVR"], True),
            "SiC multi-temperature SVR": export_material(models["SiC multi-temperature SVR"], True),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes) with {len(payload['models'])} estimators")
    print(f"Export Python {sys.version.split()[0]} / scikit-learn {sklearn.__version__}")

if __name__ == "__main__":
    main()
