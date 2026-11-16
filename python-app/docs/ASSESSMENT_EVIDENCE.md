# DiodeLab — assessment evidence map

This map follows the supplied marking rubric. It identifies evidence included in this repository and makes qualifications visible. It does not predict or guarantee a grade.

## Shared ML reasoning — 80 points

### 1. Problem formulation and scope — 10 points

**Question.** How closely can regression models estimate diode current from measured voltage for a 1N4004 diode, and how do measured I–V responses of selected silicon and silicon-carbide devices vary with voltage and recorded temperature?

**Target and units.** The primary target is current in amperes (A). Voltage is in volts (V); material-specific inputs additionally include device identity and temperature in kelvin (K). One record is one measured I–V point, not one independent device.

**Scope.** The application is an educational predictor over supplied measured devices and conditions. Model outputs are estimates, not physical measurements. It does not establish performance on unseen devices, unmeasured temperatures or unsupported extrapolation regions.

**Evidence:** `README.md`, `app.py`, `notebooks/README.md`, `docs/REPRODUCIBILITY.md`.

### 2. Data understanding — 10 points

- `diode_iv_data.csv`: 170 cleaned 1N4004 measured voltage/current pairs.
- `data/processed/classified_diode_measurements.csv`: 720 rows, 13 devices (9 silicon, 4 SiC), with 77 K and 293 K measurements.
- `data/processed/external_iv_measurements_review.csv`: 533 reviewed external measurement rows.
- `data/external/cryogenic_diode_measurements.csv`: 4,201 rows in the supplied cryogenic source collection.

Data-source, attribution, and license notes are in `data/external/README.md` and `data/external/cryogenic_dataset_README.md`. Row meanings, variables, missing-value handling and low-current cautions are described in `README.md` and `docs/REPRODUCIBILITY.md`.

### 3. Preprocessing and statistical reasoning — 10 points

The included workflows drop incomplete rows required for each experiment, restrict log-current models to positive currents, and preserve device and measured temperature as predictors where applicable. Material model preprocessing uses a `ColumnTransformer`/pipeline containing `StandardScaler` and `OneHotEncoder`; the preprocessing estimators are fit as part of the training pipeline, not on the held-out test rows. The final multi-temperature workflow uses `TransformedTargetRegressor` with a `log10` target transform and inverse transformation.

**Statistical qualification:** the voltage-ordered material experiment splits each device curve separately so later voltage points are held out. Random-split and voltage-ordered results answer different generalization questions and should not be presented as interchangeable.

**Evidence:** original notebooks, `scripts/reproduce_evaluation.py`, split manifests and tuning manifests in `evaluation_outputs/materials/`.

### 4. Baseline and method selection — 15 points

The 1N4004 benchmark compares a mean baseline, Linear Regression, Random Forest and tuned RBF SVR. RF has the lowest recorded MAE; tuned SVR has the lowest recorded RMSE and highest R². The material evaluation outputs also include a supplementary mean baseline for the final multi-temperature split. The standard material SVR notebook selects separate C values for Silicon and SiC using an inner validation region.

**Evidence:** notebook outputs, `evaluation_outputs/1n4004/random_test_metrics.csv`, `evaluation_outputs/materials/standard_material_tuning_grid_validation.csv`, `evaluation_outputs/materials/material_multi_temperature_metrics_with_baseline.csv`.

### 5. Evaluation design and metrics — 20 points

The 1N4004 random experiment uses 102/34/34 train/validation/test rows, `random_state=42`, and three-fold GridSearchCV on training data. A second 1N4004 experiment trains on the first 60% of voltage-sorted observations and reports validation on the next 20%; the final 20% is unused in that notebook comparison.

The standard Si/SiC SVR design creates a voltage-ordered split within each device: first 80% for outer training and last 20% for held-out testing. Hyperparameters are chosen using a nested per-device validation segment inside the outer training portion. The final multi-temperature design uses an 80/20 random split with `random_state=42`.

MAE is interpretable as average absolute error in amperes; RMSE gives greater weight to large errors; R² measures variation explained relative to a constant-mean predictor on the metric's target scale. `evaluation_outputs/` stores split manifests, metrics and the actual/predicted pairs used to calculate the corresponding residual evidence.

**Version qualification:** the included outputs were generated in Python 3.13.5 / scikit-learn 1.8.0 because that was the available audit runtime. The repository pins Python 3.11 and scikit-learn 1.6.1. The output metadata and comparison CSVs explicitly identify this mismatch. Re-run the script under the pinned environment before claiming strict version-matched reproduction.

### 6. Results, errors and limitations — 10 points

The repository now contains row-level actual/predicted/residual exports and residual plots for:

- 1N4004 random-holdout RF, tuned SVR, Linear Regression and mean baseline;
- 1N4004 voltage-ordered validation models;
- reverse-bias SVR's eight selected test rows (using the packaged original untuned artifact);
- standard Silicon/SiC per-device voltage-ordered SVR tests;
- final multi-temperature Silicon/SiC random-split SVR tests.

These are generated evaluation artifacts, not synthetic residuals. Their runtime and notebook comparison qualifications are in `evaluation_outputs/run_metadata.json` and relevant CSVs. The SiC standard voltage-ordered and SiC multi-temperature results differ slightly from notebook outputs in the 1.8.0 diagnostic run; the SiC comparison files flag this. Do not claim exact match until rerun with 1.6.1.

Scientific limitations include voltage correlation within sweeps, limited devices, only two recorded temperatures, unsupported extrapolation, no independent-device holdout, no confidence intervals, archived Colab notebook dependencies, and the idealized Shockley helper's omitted physical effects. See `docs/LIMITATIONS_AND_FUTURE_WORK.md`.

### 7. Reproducibility and technical integrity — 5 points

Included evidence:

- `requirements.txt` pins scikit-learn 1.6.1; `runtime.txt` specifies Python 3.11.
- Original notebooks and source/data documentation are retained.
- `scripts/check_environment.py` checks the active runtime.
- `scripts/reproduce_evaluation.py` regenerates selected experiment split manifests, prediction/residual tables, metrics, plots and runtime metadata.
- `SHA256SUMS.txt` provides file-integrity hashes for the packaged project files.

**Remaining boundary:** this is not a full clean-room pipeline that retrains every released `.joblib` artifact from raw inputs. The original notebooks are iterative Colab work logs with manual uploads, absolute paths and superseded cells. The evaluation script loads some saved artifacts and refits the notebook-defined material experiments; its scope and limitations are documented. A strict pinned-environment run is still required because this package's generated evidence is labelled as a 1.8.0 diagnostic run.

## ES 335 undergraduate deliverable — 20 points

### Interactive website — 10 points

The published GitHub Pages website is the static project landing page, and the complete interactive Streamlit application is hosted separately. The two links and their distinct roles are explicit in `README.md` and `index.html`. The app includes Home, Project Guide, Predictor, Model Comparison and Dataset Explorer pages.

**Important deployment interpretation:** if the tutor requires the complete interactive Python predictor to run under the GitHub Pages domain itself, that is not achieved by this current Streamlit deployment. GitHub Pages does not execute Python. The selected next phase is a separate browser-native migration; it is not part of this submission ZIP.

### Useful interaction — 5 points

The Streamlit application provides device, model and measured-temperature selection, prediction controls, interactive I–V plots, model comparison, dataset browsing and CSV inspection. These interactions help visitors examine predictions and measurements rather than serving only as decoration.

### Individual understanding and defense — 5 points

`docs/INDIVIDUAL_DEFENSE.md` contains an evidence-based draft of the project contribution, likely tutor questions, technical answer frameworks and a demonstration sequence. The student must review and edit the personal-contribution claims to match their exact work and be prepared to explain the modelling decisions in their own words.

## Submission integrity statement

This repository includes both positive evidence and explicit qualifications. Do not claim that the random-split scores prove generalization to unseen devices, that the reverse-bias model artifact is tuned, that all saved models were independently retrained, or that the diagnostic 1.8.0 run is a strict reproduction under the pinned 1.6.1 environment.
