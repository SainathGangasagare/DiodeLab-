# Notebook archive and experiment guide

The two original Colab notebooks are preserved here as uploaded. They have not
been rewritten or represented as clean, one-click notebooks.

## `ML_PROJECT.ipynb` — original 1N4004 experiment

This notebook documents the initial 1N4004 forward-bias workflow: public data
retrieval, data inspection and cleaning, voltage-ordered validation, a random
train/validation/test experiment, baseline/model comparison, SVR tuning, and
saving the Random Forest and tuned SVR estimators.

Key details in the saved cells and outputs:

- The source CSV has 171 rows; `v_meas` and `i_meas` each have one missing
  value. Dropping the missing measurement pair leaves 170 rows.
- The random experiment first reserves 20% for test with `random_state=42`,
  then reserves 25% of the remaining data for validation. Displayed split
  sizes are 102 train, 34 validation, and 34 test rows.
- Models include a mean baseline, Linear Regression, Random Forest, and SVR.
  The tuned SVR search uses a three-fold `GridSearchCV` on training data.
- Its final test outputs agree with the 1N4004 metrics displayed in the app:
  - Random Forest: MAE 0.0001714702 A, RMSE 0.0004224828 A, R² 0.9989055.
  - Tuned SVR: MAE 0.0002631377 A, RMSE 0.0003458506 A, R² 0.9992665.
  - Linear Regression: MAE 0.006944 A, RMSE 0.009559 A, R² 0.439677.
  - Mean baseline: MAE 0.008777 A, RMSE 0.012815 A, R² -0.007052.

The notebook also contains early exploratory and superseded cells. Do not run
every cell blindly from top to bottom; use the cells documenting the final
random-split experiment and tuned-SVR test evaluation as the reference.

## `FINAL_BOSS_ML.ipynb` — expanded data and model experiments

This larger notebook documents external/cryogenic data inspection, device and
material classification, measurement-quality checks, material-specific
regression, error analysis, multi-temperature SVR experiments, and a
1N4004 reverse-bias experiment.

Key details in its saved outputs:

- The positive-current rows for the final multi-temperature work comprise
  474 Silicon measurements and 220 Silicon Carbide measurements across 9 and
  4 devices, respectively, at 77 K and 293 K.
- The corrected multi-temperature training code is cell index 347
  (cell 348 when counted from 1). It uses an 80/20 random split with
  `random_state=42`, one-hot encodes device, scales voltage and temperature,
  uses an RBF SVR, transforms the target with `log10`, and inverts the
  transformation with the named `inverse_log_current` function. It fits on
  `X_train, y_train`, saves the model, reloads it and checks sample predictions.
- The saved output reports:
  - Silicon: MAE 0.974620 A, RMSE 2.241743 A, R² 0.995511 (95 test rows).
  - Silicon Carbide: MAE 0.187943 A, RMSE 0.251970 A, R² 0.998697 (44 test rows).
- A later evaluation cell reports MAE relative to median test current as
  10.302535% for Silicon and 2.195081% for SiC.
- The notebook also records exploratory GaN analysis and an experimental
  GaN fit. GaN is excluded from the released website and active app dataset,
  but the historical experiment remains in this original notebook. Do not
  describe GaN as a supported deployed model or say that no GaN experiment
  ever took place.
- The reverse-bias experiment starts with 41 rows, excludes 3 non-positive
  current rows, and uses 8 selected test rows from sorted measurements,
  leaving 30 training rows.

## Important rerun caveats

1. Both notebooks are iterative Colab work logs, not polished `Run all`
   pipelines. They contain repeated and superseded cells, Colab-specific
   `files.upload()` / `files.download()` calls, shell or notebook magics, and
   absolute `/content/...` paths. Some cells expect uploaded files or variables
   created in earlier manual steps.
2. `FINAL_BOSS_ML.ipynb` has saved outputs but no Markdown cells and no
   execution-count metadata. Outputs are useful historical evidence, but cell
   order alone is not a clean-room reproducibility guarantee.
3. In the reverse-bias experiment, the tuning result is assigned to
   `best_svr`, but the final save cell serializes `svr_model`, the original
   untuned SVR. The packaged reverse-bias estimator must not be described as
   tuned based on this notebook unless the save cell is corrected and the
   artifact regenerated.
4. Earlier multi-temperature cells precede the corrected cell 348 (1-based).
   Prefer cell 348 for the final Silicon/SiC training procedure; earlier
   variants include superseded target transformations or a fitting mistake.
5. The notebooks document split configurations and seeds, but do not export
   explicit row-ID split manifests or complete per-row prediction/residual
   tables for every final model.

## Recommended use

Read the original notebooks as the experiment history. Use `ML_PROJECT.ipynb`
to trace the 1N4004 benchmark; use cell 348 and the subsequent evaluation
cells in `FINAL_BOSS_ML.ipynb` to trace the released Silicon/SiC
multi-temperature estimators. A clean reproduction pass should replace
Colab-only paths/uploads with repository-relative paths and export split
manifests plus prediction-level results.

## Recreated evaluation artifacts

The repository now includes `scripts/reproduce_evaluation.py` and generated outputs under `evaluation_outputs/`. The script recreates selected reported evaluation designs and exports row-level predictions/residuals rather than relying only on aggregate notebook metrics:

- `evaluation_outputs/1n4004/`: random holdout and voltage-ordered validation.
- `evaluation_outputs/1n4004_reverse_bias/`: eight selected reverse-bias test rows using the packaged original untuned artifact.
- `evaluation_outputs/materials/`: final multi-temperature random split plus standard SVR per-device voltage-ordered evaluation, including nested tuning/validation results.

Read `evaluation_outputs/README.md`, `evaluation_outputs/run_metadata.json`, and `docs/REPRODUCIBILITY.md` before interpreting the generated results. The current saved outputs were produced in Python 3.13.5 / scikit-learn 1.8.0, not the project-pinned Python 3.11 / scikit-learn 1.6.1 environment. Some notebook comparisons match to the displayed precision; the SiC comparisons differ slightly. A pinned-environment rerun is required for strict version-matched verification.
