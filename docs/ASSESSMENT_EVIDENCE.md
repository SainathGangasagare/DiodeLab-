# DiodeLab — assessment evidence map

This map follows the supplied marking rubric. It identifies evidence included in this repository and makes qualifications visible. It does not predict or guarantee a grade.

## Shared ML reasoning — 80 points

### 1. Problem formulation and scope — 10 points

**Question.** How closely can regression models estimate diode current from measured voltage for a 1N4004 diode, and how do measured I–V responses of selected silicon and silicon-carbide devices vary with voltage and recorded temperature?

**Target and units.** The primary target is current in amperes (A). Voltage is in volts (V); material-specific inputs additionally include device identity and temperature in kelvin (K). One record is one measured I–V point, not one independent device.

**Scope.** The application is an educational predictor over supplied measured devices and conditions. Model outputs are estimates, not physical measurements. It does not establish performance on unseen devices, unmeasured temperatures or unsupported extrapolation regions.

**Evidence:** `python-app/README.md`, `python-app/app.py`, `python-app/notebooks/README.md`, this folder’s `REPRODUCIBILITY.md`.

### 2. Data understanding — 10 points

- `python-app/diode_iv_data.csv`: 170 cleaned 1N4004 measured voltage/current pairs.
- `python-app/data/processed/classified_diode_measurements.csv`: 720 rows, 13 devices (9 silicon, 4 SiC), with 77 K and 293 K measurements.
- `python-app/data/processed/external_iv_measurements_review.csv`: 533 reviewed external measurement rows.
- `python-app/data/external/cryogenic_diode_measurements.csv`: 4,201 rows in the supplied cryogenic source collection.

Data-source, attribution, and license notes are in `python-app/data/external/README.md` and `python-app/data/external/cryogenic_dataset_README.md`. Row meanings, variables, missing-value handling and low-current cautions are described in `python-app/README.md` and `docs/REPRODUCIBILITY.md`.

### 3. Preprocessing and statistical reasoning — 10 points

The included workflows drop incomplete rows required for each experiment, restrict log-current models to positive currents, and preserve device and measured temperature as predictors where applicable. Material model preprocessing uses a `ColumnTransformer`/pipeline containing `StandardScaler` and `OneHotEncoder`; the preprocessing estimators are fit as part of the training pipeline, not on the held-out test rows. The final multi-temperature workflow uses `TransformedTargetRegressor` with a `log10` target transform and inverse transformation.

**Statistical qualification:** the voltage-ordered material experiment splits each device curve separately so later voltage points are held out. Random-split and voltage-ordered results answer different generalization questions and should not be presented as interchangeable.

**Evidence:** original notebooks in `python-app/notebooks/`, `python-app/scripts/reproduce_evaluation.py`, split manifests and tuning manifests in `python-app/evaluation_outputs/materials/`.

### 4. Baseline and method selection — 15 points

The 1N4004 benchmark compares a mean baseline, Linear Regression, Random Forest and tuned RBF SVR. RF has the lowest recorded MAE; tuned SVR has the lowest recorded RMSE and highest R². The material evaluation outputs also include a supplementary mean baseline for the final multi-temperature split. The standard material SVR notebook selects separate C values for Silicon and SiC using an inner validation region.

**Evidence:** notebook outputs, `python-app/evaluation_outputs/1n4004/random_test_metrics.csv`, `python-app/evaluation_outputs/materials/standard_material_tuning_grid_validation.csv`, `python-app/evaluation_outputs/materials/material_multi_temperature_metrics_with_baseline.csv`.

### 5. Evaluation design and metrics — 20 points

The 1N4004 random experiment uses 102/34/34 train/validation/test rows, `random_state=42`, and three-fold GridSearchCV on training data. A second 1N4004 experiment trains on the first 60% of voltage-sorted observations and reports validation on the next 20%; the final 20% is unused in that notebook comparison.

The standard Si/SiC SVR design creates a voltage-ordered split within each device: first 80% for outer training and last 20% for held-out testing. Hyperparameters are chosen using a nested per-device validation segment inside the outer training portion. The final multi-temperature design uses an 80/20 random split with `random_state=42`.

MAE is interpretable as average absolute error in amperes; RMSE gives greater weight to large errors; R² measures variation explained relative to a constant-mean predictor on the metric's target scale. `python-app/evaluation_outputs/` stores split manifests, metrics and the actual/predicted pairs used to calculate the corresponding residual evidence.

### 6. Results, errors and limitations — 10 points

The repository now contains row-level actual/predicted/residual exports and residual plots for:

- 1N4004 random-holdout RF, tuned SVR, Linear Regression and mean baseline;
- 1N4004 voltage-ordered validation models;
- reverse-bias SVR's eight selected test rows (using the packaged original untuned artifact);
- standard Silicon/SiC per-device voltage-ordered SVR tests;
- final multi-temperature Silicon/SiC random-split SVR tests.

These are generated evaluation artifacts, not synthetic residuals. The associated metadata and comparison files are included alongside the outputs so the evaluation process and recorded results can be inspected.

Scientific limitations include voltage correlation within sweeps, limited devices, only two recorded temperatures, unsupported extrapolation, no independent-device holdout, no confidence intervals, archived Colab notebook dependencies, and the idealized Shockley helper's omitted physical effects. See `docs/LIMITATIONS_AND_FUTURE_WORK.md`.

### 7. Reproducibility and technical integrity — 5 points

Included evidence:

- `python-app/requirements.txt` and `python-app/runtime.txt` document the environment for running the preserved original Python application.
- Original notebooks and source/data documentation are retained.
- `python-app/scripts/check_environment.py` checks the active runtime.
- `python-app/scripts/reproduce_evaluation.py` regenerates selected experiment split manifests, prediction/residual tables, metrics, plots and runtime metadata.
- `python-app/SHA256SUMS.txt` provides file-integrity hashes for the packaged project files.

**Remaining boundary:** this is not a full clean-room pipeline that retrains every released `.joblib` artifact from raw inputs. The original notebooks are iterative Colab work logs with manual uploads, absolute paths and superseded cells. The evaluation script loads some saved artifacts and refits the notebook-defined material experiments; its scope and limitations are documented. The scripts and archived notebooks document the selected evaluation workflows and their outputs.

## ES 335 undergraduate deliverable — 20 points

### Interactive website — 10 points

This package contains a browser-native website served from the repository root on GitHub Pages. It implements the five project areas: Home, Project Guide, Predictor, Model Comparison and Dataset Explorer. Unlike the original Streamlit deployment, the GitHub Pages build runs in the browser and does not require a Python server. The root `README.md`, `GITHUB_PAGES_MIGRATION.md` and `SITE_VALIDATION.md` explain the deployment architecture and verification boundaries.

The Predictor uses browser-exported parameters from the seven original saved estimators. `SITE_VALIDATION.md` records a 215-input Python-versus-JavaScript parity check with zero failures. That parity test validates the model calculations on the sampled inputs; it is not a substitute for testing the published site in the instructor’s browser. A pixel-for-pixel screenshot comparison could not be completed in the build environment and should not be claimed.

### Useful interaction — 5 points

The browser application provides device/model/temperature selection, current prediction controls, I–V plots, selected-voltage markers and comparison options, model comparison views, dataset selection/filtering, table preview and CSV download. The original Python source and its saved estimator artifacts are preserved under `python-app/`. The site-validation record documents static checks; the published site should still be opened and its controls manually tested before submission.

### Individual understanding and defense — 5 points

`docs/INDIVIDUAL_DEFENSE.md` contains an evidence-based draft of the project contribution, likely tutor questions, technical answer frameworks and a demonstration sequence. The student must review and edit the personal-contribution claims to match their exact work and be prepared to explain the modelling decisions in their own words.

## Submission integrity statement

This repository includes both positive evidence and explicit qualifications. Do not claim that the random-split scores prove generalization to unseen devices, that the reverse-bias model artifact is tuned, that all saved models were independently retrained, or that selected evaluation scripts retrain every saved estimator from raw data.
