#!/usr/bin/env python3
"""Recreate DiodeLab evaluation tables, split manifests and residual evidence.

The original notebook procedures are reproduced as closely as the supplied
artifacts allow. The expected runtime is Python 3.11 with scikit-learn 1.6.1.
Use --allow-version-mismatch only for a clearly labelled diagnostic run.
Outputs are written to evaluation_outputs/ relative to the project root.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor

EXPECTED_SKLEARN = "1.6.1"


def inverse_log_current(values: np.ndarray) -> np.ndarray:
    """Named inverse used by the notebook's TransformedTargetRegressor."""
    return np.power(10.0, values)


def metric_row(name: str, actual: np.ndarray, predicted: np.ndarray,
               *, r2_target: np.ndarray | None = None) -> dict[str, Any]:
    actual = np.asarray(actual, dtype=float).reshape(-1)
    predicted = np.asarray(predicted, dtype=float).reshape(-1)
    target_for_r2 = actual if r2_target is None else np.asarray(r2_target, dtype=float).reshape(-1)
    pred_for_r2 = predicted if r2_target is None else np.log10(np.maximum(predicted, np.finfo(float).tiny))
    return {
        "model": name,
        "test_rows": int(len(actual)),
        "MAE_A": float(mean_absolute_error(actual, predicted)),
        "RMSE_A": float(np.sqrt(mean_squared_error(actual, predicted))),
        "R2": float(r2_score(target_for_r2, pred_for_r2)),
    }


def write_plot(frame: pd.DataFrame, x_col: str, groups: list[str], title: str,
               destination: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    for label in groups:
        part = frame[frame["model"] == label].sort_values(x_col)
        if not part.empty:
            ax.scatter(part[x_col], part["residual_A"], s=22, alpha=0.8, label=label)
    ax.axhline(0.0, linewidth=1, linestyle="--")
    ax.set_xlabel(x_col.replace("_", " "))
    ax.set_ylabel("Residual (A) = actual - predicted")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def save_manifest(records: list[dict[str, Any]], path: Path) -> None:
    pd.DataFrame(records).to_csv(path, index=False)


def run_1n4004_random(root: Path, out: Path, warning_log: list[str]) -> list[dict[str, Any]]:
    data = pd.read_csv(root / "diode_iv_data.csv")
    data = data.dropna(subset=["v_meas", "i_meas"])[["v_meas", "i_meas"]]
    data = data.sort_values("v_meas").reset_index(drop=True)
    data.insert(0, "row_id", np.arange(len(data)))
    if len(data) != 170:
        raise ValueError(f"Expected 170 cleaned 1N4004 rows; found {len(data)}")

    ids = data["row_id"].to_numpy()
    trainval_ids, test_ids = train_test_split(ids, test_size=0.20, random_state=42)
    train_ids, validation_ids = train_test_split(
        trainval_ids, test_size=0.25, random_state=42
    )
    split_for = {int(i): "train" for i in train_ids}
    split_for.update({int(i): "validation" for i in validation_ids})
    split_for.update({int(i): "test" for i in test_ids})
    manifest = data[["row_id", "v_meas", "i_meas"]].copy()
    manifest["split"] = manifest["row_id"].map(split_for)
    manifest.to_csv(out / "random_split_manifest.csv", index=False)

    train = data.set_index("row_id").loc[train_ids]
    validation = data.set_index("row_id").loc[validation_ids]
    test = data.set_index("row_id").loc[test_ids]
    X_train, y_train = train[["v_meas"]], train["i_meas"].to_numpy()
    X_validation, y_validation = validation[["v_meas"]], validation["i_meas"].to_numpy()
    X_test, y_test = test[["v_meas"]], test["i_meas"].to_numpy()

    models: dict[str, Any] = {}
    for name, filename in [
        ("Random Forest", "random_forest_model.joblib"),
        ("Tuned SVR", "tuned_svr_model.joblib"),
    ]:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            models[name] = joblib.load(root / filename)
        warning_log.extend(f"{filename}: {w.message}" for w in captured)

    # The original notebook fits these two baselines on the same random training rows.
    models["Linear Regression"] = LinearRegression().fit(X_train, y_train)
    models["Mean baseline"] = DummyRegressor(strategy="mean").fit(X_train, y_train)

    rows: list[pd.DataFrame] = []
    metrics: list[dict[str, Any]] = []
    expected = {
        "Random Forest": (0.00017147018342764475, 0.0004224828434410085, 0.9989054838122119),
        "Tuned SVR": (0.00026313774398049986, 0.0003458506091701, 0.9992665320790979),
        "Linear Regression": (0.006944, 0.009559, 0.439677),
        "Mean baseline": (0.008777, 0.012815, -0.007052),
    }
    for name, model in models.items():
        pred = np.asarray(model.predict(X_test)).reshape(-1)
        actual = y_test
        residual = actual - pred
        item = metric_row(name, actual, pred)
        item["notebook_MAE_A"] = expected[name][0]
        item["notebook_RMSE_A"] = expected[name][1]
        item["notebook_R2"] = expected[name][2]
        metrics.append(item)
        rows.append(pd.DataFrame({
            "row_id": test.index.to_numpy(), "voltage_V": X_test["v_meas"].to_numpy(),
            "actual_current_A": actual, "predicted_current_A": pred,
            "residual_A": residual, "absolute_error_A": np.abs(residual),
            "model": name,
        }))
    predictions = pd.concat(rows, ignore_index=True)
    predictions.to_csv(out / "random_test_predictions_residuals.csv", index=False)
    pd.DataFrame(metrics).to_csv(out / "random_test_metrics.csv", index=False)
    tuned_validation_pred = np.asarray(models["Tuned SVR"].predict(X_validation)).reshape(-1)
    search_pipeline = Pipeline([
        ("standardscaler", StandardScaler()),
        ("svr", SVR(kernel="rbf")),
    ])
    search_grid = {
        "svr__C": [1, 10, 100, 1000],
        "svr__epsilon": [0.0001, 0.001, 0.005],
        "svr__gamma": ["scale", 0.1, 1],
    }
    search = GridSearchCV(
        search_pipeline, search_grid, scoring="neg_mean_absolute_error", cv=3
    )
    search.fit(X_train, y_train)
    cv_table = pd.DataFrame(search.cv_results_)
    keep_cols = [c for c in [
        "param_svr__C", "param_svr__epsilon", "param_svr__gamma",
        "mean_test_score", "std_test_score", "rank_test_score"
    ] if c in cv_table.columns]
    cv_table[keep_cols].to_csv(out / "grid_search_cv_results.csv", index=False)
    notebook_best = {"svr__C": 100, "svr__epsilon": 0.0001, "svr__gamma": 1}
    recomputed_best = dict(search.best_params_)
    grid_best_test_pred = np.asarray(search.best_estimator_.predict(X_test)).reshape(-1)
    packaged_test_pred = np.asarray(models["Tuned SVR"].predict(X_test)).reshape(-1)
    grid_best_validation_pred = np.asarray(search.best_estimator_.predict(X_validation)).reshape(-1)
    refit_rf = RandomForestRegressor(n_estimators=200, random_state=42).fit(X_train, y_train)
    refit_rf_test_pred = np.asarray(refit_rf.predict(X_test)).reshape(-1)
    packaged_rf_test_pred = np.asarray(models["Random Forest"].predict(X_test)).reshape(-1)
    tuning_record = {
        "experiment": "1N4004 random split, tuned RBF SVR",
        "training_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_rows": int(len(test)),
        "random_state": 42,
        "split_procedure": "20% final test split; then 25% of remaining rows for validation",
        "pipeline": "StandardScaler + SVR(kernel='rbf')",
        "grid": {
            "C": [1, 10, 100, 1000],
            "epsilon": [0.0001, 0.001, 0.005],
            "gamma": ["scale", 0.1, 1],
        },
        "cv_folds": 3,
        "scoring": "negative mean absolute error",
        "selected_parameters_from_notebook": {
            "C": 100, "epsilon": 0.0001, "gamma": 1
        },
        "recomputed_best_parameters_in_current_runtime": recomputed_best,
        "recomputed_best_parameters_match_notebook": recomputed_best == notebook_best,
        "recomputed_best_cv_MAE_A": float(-search.best_score_),
        "notebook_best_cv_MAE_A": 0.0002689237422945725,
        "max_abs_test_prediction_difference_packaged_vs_recomputed_A": float(np.max(np.abs(packaged_test_pred - grid_best_test_pred))),
        "max_abs_validation_prediction_difference_packaged_vs_recomputed_A": float(np.max(np.abs(tuned_validation_pred - grid_best_validation_pred))),
        "max_abs_random_forest_test_prediction_difference_packaged_vs_retrained_A": float(np.max(np.abs(packaged_rf_test_pred - refit_rf_test_pred))),
        "validation_metrics_from_packaged_estimator": {
            "MAE_A": float(mean_absolute_error(y_validation, tuned_validation_pred)),
            "RMSE_A": float(np.sqrt(mean_squared_error(y_validation, tuned_validation_pred))),
            "R2": float(r2_score(y_validation, tuned_validation_pred)),
        },
        "note": "The script reruns the notebook's three-fold GridSearchCV on the reconstructed training partition and exports all candidate CV results. Test metrics are calculated from the packaged tuned_svr_model.joblib artifact so the evaluation refers to the distributed estimator. The validation metrics are also calculated from that packaged estimator. Compare the recomputed best parameters and CV score with the notebook record."
    }
    (out / "tuning_record.json").write_text(json.dumps(tuning_record, indent=2), encoding="utf-8")
    write_plot(predictions, "voltage_V", list(models),
               "1N4004 random-split test residuals", out / "random_test_residuals_vs_voltage.png")
    return metrics


def run_1n4004_voltage_ordered(root: Path, out: Path) -> list[dict[str, Any]]:
    data = pd.read_csv(root / "diode_iv_data.csv")
    data = data.dropna(subset=["v_meas", "i_meas"])[["v_meas", "i_meas"]]
    data = data.sort_values("v_meas").reset_index(drop=True)
    data.insert(0, "row_id", np.arange(len(data)))
    n = len(data)
    train_end, validation_end = int(0.60 * n), int(0.80 * n)
    train = data.iloc[:train_end].copy()
    validation = data.iloc[train_end:validation_end].copy()
    manifest = data[["row_id", "v_meas", "i_meas"]].copy()
    manifest["split"] = ["train"] * len(train) + ["validation"] * len(validation) + ["test (unused in this notebook comparison)"] * (n - validation_end)
    manifest.to_csv(out / "voltage_ordered_split_manifest.csv", index=False)

    X_train, y_train = train[["v_meas"]], train["i_meas"].to_numpy()
    X_val, y_val = validation[["v_meas"]], validation["i_meas"].to_numpy()
    models = {
        "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
        "Linear Regression": LinearRegression(),
        "Mean baseline": DummyRegressor(strategy="mean"),
    }
    frames, metrics = [], []
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_val)
        residual = y_val - pred
        metrics.append(metric_row(name, y_val, pred))
        frames.append(pd.DataFrame({
            "row_id": validation["row_id"].to_numpy(),
            "voltage_V": X_val["v_meas"].to_numpy(),
            "actual_current_A": y_val, "predicted_current_A": pred,
            "residual_A": residual, "absolute_error_A": np.abs(residual),
            "model": name,
        }))
    predictions = pd.concat(frames, ignore_index=True)
    predictions.to_csv(out / "voltage_ordered_validation_predictions_residuals.csv", index=False)
    pd.DataFrame(metrics).to_csv(out / "voltage_ordered_validation_metrics.csv", index=False)
    write_plot(predictions, "voltage_V", list(models),
               "1N4004 voltage-ordered validation residuals",
               out / "voltage_ordered_validation_residuals_vs_voltage.png")
    return metrics


def run_reverse_bias(root: Path, out: Path, warning_log: list[str]) -> list[dict[str, Any]]:
    data = pd.read_csv(root / "data" / "external" / "1n4004_reverse.csv")
    data = data.copy()
    data["source_row_id"] = data.index
    data = data[data["i_meas"] > 0].sort_values("v_meas").reset_index(drop=True)
    if len(data) != 38:
        raise ValueError(f"Expected 38 positive-current reverse-bias rows; found {len(data)}")
    test_positions = np.array(list(range(2, 38, 5)), dtype=int)
    train_positions = np.array([i for i in range(len(data)) if i not in set(test_positions)], dtype=int)
    data["split"] = "train"
    data.loc[test_positions, "split"] = "test"
    data.to_csv(out / "reverse_bias_split_manifest.csv", index=False)
    test = data.iloc[test_positions]
    X_test = test[["v_meas"]]
    y_actual = test["i_meas"].to_numpy()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model = joblib.load(root / "1n4004_reverse_svr_model.joblib")
    warning_log.extend(f"1n4004_reverse_svr_model.joblib: {w.message}" for w in captured)
    predicted_log = np.asarray(model.predict(X_test)).reshape(-1)
    predicted = np.power(10.0, predicted_log)
    residual = y_actual - predicted
    frame = pd.DataFrame({
        "cleaned_row_id": test.index.to_numpy(),
        "source_row_id": test["source_row_id"].to_numpy(),
        "voltage_V": test["v_meas"].to_numpy(),
        "actual_current_A": y_actual,
        "predicted_current_A": predicted,
        "residual_A": residual,
        "absolute_error_A": np.abs(residual),
        "actual_log10_current": np.log10(y_actual),
        "predicted_log10_current": predicted_log,
    })
    frame.to_csv(out / "reverse_bias_test_predictions_residuals.csv", index=False)
    result = {
        "model": "Reverse-bias SVR (packaged artifact; original untuned pipeline)",
        "test_rows": len(frame),
        "MAE_A": float(mean_absolute_error(y_actual, predicted)),
        "RMSE_A": float(np.sqrt(mean_squared_error(y_actual, predicted))),
        "R2_log10_current": float(r2_score(np.log10(y_actual), predicted_log)),
        "mean_absolute_percentage_error": float(np.mean(np.abs(residual) / y_actual) * 100),
    }
    pd.DataFrame([result]).to_csv(out / "reverse_bias_metrics.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.scatter(frame["voltage_V"], frame["residual_A"], s=28)
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("Reverse measured voltage (V)")
    ax.set_ylabel("Residual (A) = actual - predicted")
    ax.set_title("1N4004 reverse-bias test residuals (8 selected rows)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "reverse_bias_test_residuals_vs_voltage.png", dpi=160)
    plt.close(fig)
    return [result]


def make_material_preprocessor() -> ColumnTransformer:
    # Column order mirrors the final multi-temperature notebook cell 348.
    return ColumnTransformer([
        ("numbers", StandardScaler(), ["voltage_V", "temperature_K"]),
        ("device", OneHotEncoder(handle_unknown="ignore"), ["device"]),
    ])


def run_material_models(root: Path, out: Path) -> list[dict[str, Any]]:
    data = pd.read_csv(root / "data" / "processed" / "classified_diode_measurements.csv")
    data = data.dropna(subset=["material", "device", "temperature_K", "voltage_V", "current_A"]).copy()
    data = data[data["current_A"] > 0].copy()
    data["source_row_id"] = data.index
    settings = {"silicon": 1, "silicon carbide": 100}
    notebook_metrics = {
        "silicon": (0.974620, 2.241743, 0.995511),
        "silicon carbide": (0.187943, 0.251970, 0.998697),
    }
    all_splits, all_predictions, metrics, comparisons = [], [], [], []
    for material, c_value in settings.items():
        subset = data[data["material"].str.lower() == material].copy()
        X = subset[["device", "voltage_V", "temperature_K"]]
        y = subset["current_A"].to_numpy()
        ids = subset["source_row_id"].to_numpy()
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X, y, ids, test_size=0.20, random_state=42
        )
        pipeline = Pipeline([
            ("preprocessor", make_material_preprocessor()),
            ("svr", SVR(kernel="rbf", C=c_value, epsilon=0.01)),
        ])
        model = TransformedTargetRegressor(
            regressor=pipeline, func=np.log10, inverse_func=inverse_log_current
        )
        model.fit(X_train, y_train)
        pred = np.asarray(model.predict(X_test)).reshape(-1)

        # A supplementary mean baseline on the same raw-current target and split.
        baseline = DummyRegressor(strategy="mean").fit(X_train, y_train)
        baseline_pred = np.asarray(baseline.predict(X_test)).reshape(-1)

        for split_name, split_ids, split_X, split_y in [
            ("train", ids_train, X_train, y_train),
            ("test", ids_test, X_test, y_test),
        ]:
            split_part = split_X.copy()
            split_part.insert(0, "source_row_id", split_ids)
            split_part.insert(1, "material", material)
            split_part["split"] = split_name
            split_part["actual_current_A"] = split_y
            all_splits.append(split_part)

        for model_name, predictions in [("Multi-temperature SVR", pred), ("Mean baseline (supplementary)", baseline_pred)]:
            residual = y_test - predictions
            result = metric_row(model_name, y_test, predictions)
            result["material"] = material
            metrics.append(result)
            frame = X_test.copy()
            frame.insert(0, "source_row_id", ids_test)
            frame.insert(1, "material", material)
            frame["actual_current_A"] = y_test
            frame["predicted_current_A"] = predictions
            frame["residual_A"] = residual
            frame["absolute_error_A"] = np.abs(residual)
            frame["model"] = model_name
            all_predictions.append(frame)
        orig = notebook_metrics[material]
        current = metric_row("Multi-temperature SVR", y_test, pred)
        for metric, notebook_value in zip(["MAE_A", "RMSE_A", "R2"], orig):
            current[f"notebook_{metric}"] = notebook_value
            current[f"absolute_difference_{metric}"] = abs(current[metric] - notebook_value)
        current["material"] = material
        current["runtime_version"] = sklearn.__version__
        current["comparison_note"] = (
            "matches notebook to displayed precision" if all(current[k] < 5e-7 for k in
                ["absolute_difference_MAE_A", "absolute_difference_RMSE_A", "absolute_difference_R2"])
            else "differs from notebook output; rerun under pinned scikit-learn 1.6.1 before treating as exact"
        )
        comparisons.append(current)

    split_df = pd.concat(all_splits, ignore_index=True)
    pred_df = pd.concat(all_predictions, ignore_index=True)
    split_df.to_csv(out / "material_multi_temperature_split_manifest.csv", index=False)
    pred_df.to_csv(out / "material_multi_temperature_test_predictions_residuals.csv", index=False)
    pd.DataFrame(metrics).to_csv(out / "material_multi_temperature_metrics_with_baseline.csv", index=False)
    pd.DataFrame(comparisons).to_csv(out / "material_notebook_metric_comparison.csv", index=False)
    for material, filename, title in [
        ("silicon", "silicon_test_residuals_vs_voltage.png", "Silicon multi-temperature residuals"),
        ("silicon carbide", "sic_test_residuals_vs_voltage.png", "Silicon-carbide multi-temperature residuals"),
    ]:
        part = pred_df[(pred_df["material"] == material) & (pred_df["model"] == "Multi-temperature SVR")]
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.scatter(part["voltage_V"], part["residual_A"], s=25, alpha=0.8)
        ax.axhline(0, linestyle="--", linewidth=1)
        ax.set_xlabel("Measured voltage (V)")
        ax.set_ylabel("Residual (A) = actual - predicted")
        ax.set_title(title + " (random 80/20 split)")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(out / filename, dpi=160)
        plt.close(fig)
    return metrics



def run_standard_material_voltage_ordered(root: Path, out: Path) -> list[dict[str, Any]]:
    """Reproduce FINAL_BOSS_ML cells 94 and 98-103 for standard Si/SiC SVR.

    The final test region is the last 20% of each device's voltage-sorted curve.
    Hyperparameters are selected on a nested validation region inside the first
    80% and then evaluated on the untouched final 20%. The notebook's cell 102
    records the selected settings and final test metrics. Cell 103 refits the
    deployable artifacts on all positive-current rows after evaluation.
    """
    data = pd.read_csv(root / "data" / "processed" / "classified_diode_measurements.csv")
    required = ["material", "device", "temperature_K", "voltage_V", "current_A"]
    data = data.dropna(subset=required).copy()
    data = data[data["current_A"] > 0].copy()
    data["source_row_id"] = data.index
    data["log10_current_A"] = np.log10(data["current_A"].astype(float))

    best_settings = {
        "silicon": {"C": 1, "epsilon": 0.01},
        "silicon carbide": {"C": 100, "epsilon": 0.01},
    }
    notebook_metrics = {
        "silicon": (4.432537, 7.032687),
        "silicon carbide": (1.389171, 1.708090),
    }
    grid_c = [1, 10, 100, 1000]
    grid_epsilon = [0.01, 0.05, 0.1]
    all_manifest, all_predictions, all_metrics, all_tuning, all_tune_splits = [], [], [], [], []

    for material, selected in best_settings.items():
        group = data[data["material"].str.lower() == material].copy()
        train_parts, test_parts = [], []
        for _, part in group.groupby("device", sort=True):
            part = part.sort_values("voltage_V")
            if len(part) < 5:
                continue
            cut = int(len(part) * 0.8)
            train_parts.append(part.iloc[:cut])
            test_parts.append(part.iloc[cut:])
        train = pd.concat(train_parts).copy()
        test = pd.concat(test_parts).copy()

        # Inner validation region: last 20% of the outer training rows per device.
        fit_parts, validation_parts = [], []
        for _, part in train.groupby("device", sort=True):
            part = part.sort_values("voltage_V")
            cut = max(3, int(len(part) * 0.8))
            fit_parts.append(part.iloc[:cut])
            validation_parts.append(part.iloc[cut:])
        fit = pd.concat(fit_parts).copy()
        validation = pd.concat(validation_parts).copy()
        tune_fit = fit[["source_row_id", "material", "device", "voltage_V", "temperature_K"]].copy()
        tune_fit["tuning_split"] = "fit"
        tune_validation = validation[["source_row_id", "material", "device", "voltage_V", "temperature_K"]].copy()
        tune_validation["tuning_split"] = "validation"
        all_tune_splits.extend([tune_fit, tune_validation])

        def build_svr(c_value: int, epsilon: float) -> Pipeline:
            preprocessor = ColumnTransformer([
                ("device", OneHotEncoder(handle_unknown="ignore"), ["device"]),
                ("numeric", StandardScaler(), ["voltage_V", "temperature_K"]),
            ])
            return Pipeline([
                ("preprocessor", preprocessor),
                ("svr", SVR(kernel="rbf", C=c_value, epsilon=epsilon)),
            ])

        tuning_rows = []
        for c_value in grid_c:
            for epsilon in grid_epsilon:
                candidate = build_svr(c_value, epsilon)
                candidate.fit(fit[["device", "voltage_V", "temperature_K"]], fit["log10_current_A"])
                validation_pred = np.power(10.0, candidate.predict(
                    validation[["device", "voltage_V", "temperature_K"]]
                ))
                tuning_rows.append({
                    "material": material, "C": c_value, "epsilon": epsilon,
                    "validation_rows": len(validation),
                    "validation_MAE_A": float(mean_absolute_error(validation["current_A"], validation_pred)),
                    "selected_in_original_notebook": bool(c_value == selected["C"] and epsilon == selected["epsilon"]),
                })
        all_tuning.extend(tuning_rows)

        # Refit chosen configuration on the complete outer train region.
        model = build_svr(selected["C"], selected["epsilon"])
        model.fit(train[["device", "voltage_V", "temperature_K"]], train["log10_current_A"])
        pred_log = model.predict(test[["device", "voltage_V", "temperature_K"]])
        pred = np.power(10.0, pred_log)
        actual = test["current_A"].to_numpy(dtype=float)
        residual = actual - pred
        result = metric_row("Standard SVR (voltage-ordered per-device test)", actual, pred,
                            r2_target=test["log10_current_A"].to_numpy())
        result.update({"material": material, "C": selected["C"], "epsilon": selected["epsilon"],
                       "notebook_MAE_A": notebook_metrics[material][0],
                       "notebook_RMSE_A": notebook_metrics[material][1],
                       "absolute_difference_MAE_A": abs(result["MAE_A"] - notebook_metrics[material][0]),
                       "absolute_difference_RMSE_A": abs(result["RMSE_A"] - notebook_metrics[material][1]),
                       "runtime_scikit_learn": sklearn.__version__,
                       "notebook_comparison": "matches displayed notebook values" if
                           abs(result["MAE_A"] - notebook_metrics[material][0]) < 5e-6 and
                           abs(result["RMSE_A"] - notebook_metrics[material][1]) < 5e-6 else
                           "differs; inspect environment and rerun with pinned 1.6.1"})
        all_metrics.append(result)

        for part_name, part in [("train", train), ("test", test)]:
            mf = part[["source_row_id", "material", "device", "voltage_V", "temperature_K", "current_A"]].copy()
            mf["split"] = part_name
            all_manifest.append(mf)
        pred_frame = test[["source_row_id", "material", "device", "voltage_V", "temperature_K"]].copy()
        pred_frame["actual_current_A"] = actual
        pred_frame["predicted_current_A"] = pred
        pred_frame["residual_A"] = residual
        pred_frame["absolute_error_A"] = np.abs(residual)
        all_predictions.append(pred_frame)

    pd.concat(all_manifest, ignore_index=True).to_csv(out / "standard_material_voltage_ordered_split_manifest.csv", index=False)
    pd.concat(all_predictions, ignore_index=True).to_csv(out / "standard_material_voltage_ordered_predictions_residuals.csv", index=False)
    pd.DataFrame(all_metrics).to_csv(out / "standard_material_voltage_ordered_metrics.csv", index=False)
    pd.DataFrame(all_tuning).to_csv(out / "standard_material_tuning_grid_validation.csv", index=False)
    pd.concat(all_tune_splits, ignore_index=True).to_csv(
        out / "standard_material_tuning_split_manifest.csv", index=False
    )
    for material, filename, title in [
        ("silicon", "standard_silicon_voltage_ordered_residuals.png", "Standard Silicon SVR: voltage-ordered residuals"),
        ("silicon carbide", "standard_sic_voltage_ordered_residuals.png", "Standard SiC SVR: voltage-ordered residuals"),
    ]:
        frame = pd.concat(all_predictions, ignore_index=True)
        part = frame[frame["material"].str.lower() == material]
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.scatter(part["voltage_V"], part["residual_A"], s=24, alpha=0.8)
        ax.axhline(0, linestyle="--", linewidth=1)
        ax.set_xlabel("Measured voltage (V)")
        ax.set_ylabel("Residual (A) = actual - predicted")
        ax.set_title(title + " (last 20% of each device curve held out)")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(out / filename, dpi=160)
        plt.close(fig)
    return all_metrics

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-version-mismatch", action="store_true",
        help="Allow a diagnostic run outside scikit-learn 1.6.1; outputs record the actual version.",
    )
    args = parser.parse_args()
    if sklearn.__version__ != EXPECTED_SKLEARN and not args.allow_version_mismatch:
        print(
            f"ERROR: expected scikit-learn {EXPECTED_SKLEARN}, found {sklearn.__version__}. "
            "Install requirements.txt or pass --allow-version-mismatch for a clearly labelled diagnostic run.",
            file=sys.stderr,
        )
        return 2

    root = Path(__file__).resolve().parents[1]
    out = root / "evaluation_outputs"
    out.mkdir(exist_ok=True)
    warning_log: list[str] = []

    print(f"Python: {sys.version.split()[0]}")
    print(f"scikit-learn: {sklearn.__version__} (project pin: {EXPECTED_SKLEARN})")
    print("Generating evaluation evidence...")
    for folder in [out / "1n4004", out / "1n4004_reverse_bias", out / "materials"]:
        folder.mkdir(parents=True, exist_ok=True)
    run_1n4004_random(root, out / "1n4004", warning_log)
    run_1n4004_voltage_ordered(root, out / "1n4004")
    run_reverse_bias(root, out / "1n4004_reverse_bias", warning_log)
    run_material_models(root, out / "materials")
    run_standard_material_voltage_ordered(root, out / "materials")

    metadata = {
        "python_version": sys.version.split()[0],
        "scikit_learn_version": sklearn.__version__,
        "project_pinned_scikit_learn_version": EXPECTED_SKLEARN,
        "version_matches_project_pin": sklearn.__version__ == EXPECTED_SKLEARN,
        "diagnostic_mismatch_override_used": bool(args.allow_version_mismatch),
        "notes": [
            "1N4004 random test predictions use the packaged RF and tuned-SVR estimators and the notebook's 102/34/34 random split.",
            "1N4004 voltage-ordered metrics are validation results from the notebook's first-60%-train / next-20%-validation design; the final 20% was not used in that comparison.",
            "Reverse-bias predictions use the packaged original, untuned SVR artifact and the notebook's eight selected test rows.",
            "Material multi-temperature models are refitted using the final notebook cell 348 recipe, on positive-current Si/SiC observations only.",
            "The material mean baseline is an additional assessment comparison and was not part of the original notebook's saved model report.",
            "Standard Si/SiC SVR uses per-device voltage-ordered outer test splits and nested per-device tuning validation as documented in FINAL_BOSS_ML.ipynb cells 94 and 98-103.",
            "When the runtime version differs from 1.6.1, all output metadata and comparison files must be read as a diagnostic run, not exact pinned-environment reproduction.",
        ],
        "joblib_load_warning_count": len(warning_log),
        "joblib_load_warning_summary": (
            "Warnings are expected in this diagnostic run because serialized estimators created with scikit-learn 1.6.1 were loaded with 1.8.0. This is not the project's pinned environment; rerun with 1.6.1 for strict compatibility verification."
            if sklearn.__version__ != EXPECTED_SKLEARN else
            "No scikit-learn version mismatch was present in the run environment."
        ),
        "joblib_load_warning_examples": sorted(set(warning_log))[:6],
        "output_folders": ["1n4004", "1n4004_reverse_bias", "materials"],
    }
    (out / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Completed. See evaluation_outputs/run_metadata.json for the exact runtime and caveats.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
