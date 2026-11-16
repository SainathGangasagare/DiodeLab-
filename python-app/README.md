# DiodeLab — diode I–V machine-learning project

DiodeLab is an educational machine-learning project for exploring measured diode current–voltage behaviour and estimating current from voltage, device identity and measured temperature within the scope of the included datasets.

## Live project links

- **GitHub Pages project website:** https://sainathgangasagare.github.io/DiodeLab/
- **Full interactive Streamlit application:** https://diodelab.streamlit.app/
- **Public source repository:** https://github.com/SainathGangasagare/DiodeLab

The GitHub Pages URL is a static project landing page. The complete Python application (Predictor, Model Comparison, Dataset Explorer and interactive plots) is currently hosted separately on Streamlit. Both links are part of the same DiodeLab submission. If the instructor requires every interaction to run under the GitHub Pages URL itself, that is a separate frontend migration and is not represented as completed in this version.

## Research questions, target and scope

1. How closely can regression models estimate the measured I–V response of a 1N4004 diode?
2. How do measured I–V curves for selected silicon and silicon-carbide power devices vary with voltage and measured temperature?

The primary prediction target is diode current in amperes (A). Inputs are measured voltage in volts (V); the material-specific models additionally use device identity and measured temperature in kelvin (K). One row in the 1N4004 dataset is one measured voltage/current pair. One row in the classified dataset is one measured point for one device at one recorded temperature. Predictions are model estimates, not new measurements. The evidence does not establish generalization to unseen devices, arbitrary temperatures or voltage regions outside the measured data.

## What the application contains

- **Home:** project overview, data scale and workflow.
- **Project Guide:** research question, data, methods, evaluation, interpretation and limitations.
- **Predictor:** saved-model estimates for supported 1N4004, silicon and silicon-carbide cases.
- **Model Comparison:** recorded 1N4004 metrics and measured-versus-predicted curve exploration for available material models.
- **Dataset Explorer:** inspection and download of supplied CSV datasets.

The active predictor does not offer GaN as a supported model. Historical exploratory GaN analysis remains documented in the original notebook archive.

## Data inventory

| File | Meaning | Rows |
|---|---|---:|
| `diode_iv_data.csv` | Cleaned 1N4004 measured voltage/current pairs | 170 |
| `data/processed/classified_diode_measurements.csv` | Silicon and SiC measurements across 13 devices | 720 |
| `data/processed/external_iv_measurements_review.csv` | Reviewed external measurements for 1N4004, 1N5229B and SB560 | 533 |
| `data/external/cryogenic_diode_measurements.csv` | Source cryogenic measurement collection | 4,201 |

The classified dataset contains 492 silicon rows and 228 silicon-carbide rows, with recorded temperatures of 77 K and 293 K. It contains 9 silicon devices and 4 SiC devices. The external review CSV is available for exploration; it is not the active material-model training table.

### Data sources and attribution

- External diode sweeps: [Diode I–V Measurements repository](https://github.com/blueberrye-io/diode-iv-measurements/). The source notes identify CC BY 4.0.
- Classified silicon/SiC device measurements: [Cryogenic and Superconducting Power Electronics Database](https://doi.org/10.57745/2AHLA6). The source notes identify Etalab Open License 2.0.

See `data/external/README.md` and `data/external/cryogenic_dataset_README.md` for source-specific provenance and caveats. Retain attribution and observe the source licenses when redistributing data.

## Preprocessing and model methods

- The 1N4004 pipeline drops rows missing measured voltage/current, sorts observations by voltage for ordered evaluation, and uses a deterministic random split for the random-holdout experiment.
- The standard Si/SiC SVR workflow removes rows missing required fields and non-positive current rows, sorts each device curve by voltage for its per-device ordered experiment, one-hot encodes device and standardizes voltage/temperature inside a fitted pipeline, and models `log10(current_A)`.
- The final multi-temperature Si/SiC workflow removes rows missing required fields and non-positive currents, uses an 80/20 random split (`random_state=42`), fits scaling and one-hot encoding on the training partition only, uses RBF SVR and a `log10` target transformation, then converts predictions back to amperes.
- The reverse-bias experiment uses positive-current rows, sorted voltage positions and a fixed eight-row test selection. The saved reverse-bias artifact is the original untuned SVR pipeline; it must not be described as the tuned estimator.

The material preprocessing and estimators are implemented as scikit-learn pipelines so the scaler and encoder are fitted using training rows rather than the held-out test rows.

## Active model inventory

The Streamlit app loads seven estimator artifacts:

| Application model | Saved artifact | Main method |
|---|---|---|
| 1N4004 Random Forest | `random_forest_model.joblib` | 200-tree Random Forest |
| 1N4004 Tuned SVR | `tuned_svr_model.joblib` | StandardScaler + RBF SVR; C=100, epsilon=0.0001, gamma=1 |
| Silicon SVR | `trained_models/silicon_svr.joblib` | Device-aware RBF SVR; C=1, epsilon=0.01 |
| SiC SVR | `trained_models/silicon_carbide_svr.joblib` | Device-aware RBF SVR; C=100, epsilon=0.01 |
| Silicon multi-temperature SVR | `trained_models/silicon_multi_temperature_svr.joblib` | RBF SVR with fitted preprocessing and log-target transform |
| SiC multi-temperature SVR | `trained_models/silicon_carbide_multi_temperature_svr.joblib` | RBF SVR with fitted preprocessing and log-target transform |
| 1N4004 reverse-bias SVR | `1n4004_reverse_svr_model.joblib` | Original untuned reverse-bias SVR pipeline |

See [`docs/MODEL_INVENTORY.md`](docs/MODEL_INVENTORY.md) for details and caveats.

## Evaluation results and interpretation

### 1N4004 random holdout

The notebook uses a 102/34/34 train/validation/test design. It first reserves 20% for test (`random_state=42`) and then reserves 25% of the remaining rows for validation. The recorded test metrics are:

| Model | MAE (A) | RMSE (A) | R² |
|---|---:|---:|---:|
| Random Forest | 0.0001714702 | 0.0004224828 | 0.9989055 |
| Tuned SVR | 0.0002631377 | 0.0003458506 | 0.9992665 |
| Linear Regression | 0.006944 | 0.009559 | 0.439677 |
| Mean baseline | 0.008777 | 0.012815 | -0.007052 |

Random Forest has the lowest recorded MAE. Tuned SVR has the lowest RMSE and highest R². The ranking depends on the metric: RMSE penalizes large errors more strongly than MAE.

### Voltage-ordered evaluation

The 1N4004 notebook also trains on the first 60% of voltage-sorted observations and evaluates on the next 20% (34 validation rows); the final 20% is not used in that notebook comparison. Random Forest validation MAE is approximately 0.001267 A with R² approximately -1.0249. This differs sharply from the random-holdout scores and illustrates that random interpolation within one measured sweep does not establish reliable performance in a later voltage region.

For standard Si/SiC SVR, the expanded notebook splits each device curve in voltage order: the first 80% of each curve forms the outer training region and the final 20% forms the held-out test region. Hyperparameter selection uses a further per-device validation region inside the outer training data. The notebook reports:

| Material | Test rows | Selected C | Epsilon | MAE (A) | RMSE (A) |
|---|---:|---:|---:|---:|---:|
| Silicon | 98 | 1 | 0.01 | 4.432537 | 7.032687 |
| Silicon carbide | 45 | 100 | 0.01 | 1.389171 | 1.708090 |

### Final multi-temperature models

The final multi-temperature notebook cell uses an 80/20 random split (`random_state=42`) and reports:

| Material | Test rows | MAE (A) | RMSE (A) | R² |
|---|---:|---:|---:|---:|
| Silicon | 95 | 0.974620 | 2.241743 | 0.995511 |
| Silicon carbide | 44 | 0.187943 | 0.251970 | 0.998697 |

These figures belong to the notebook's final multi-temperature experiment and should not be conflated with the separate voltage-ordered per-device evaluation above.

## Evaluation artifacts included in this repository

The repository now includes a repository-relative evaluation script and row-level evidence under `evaluation_outputs/`:

- `evaluation_outputs/1n4004/`: random split manifest, test metrics, row-level test predictions/residuals, a residual plot, `tuning_record.json` and the full three-fold `grid_search_cv_results.csv`; plus the voltage-ordered validation manifest, metrics, row-level predictions/residuals and residual plot.
- `evaluation_outputs/1n4004_reverse_bias/`: deterministic split manifest, eight held-out predictions/residuals, metrics and residual plot for the packaged original untuned reverse-bias artifact.
- `evaluation_outputs/materials/`: random split manifests, multi-temperature test predictions/residuals and plots, standard per-device voltage-ordered train/test and tuning manifests, tuning-grid validation results, standard-model residuals/plots, and comparisons with saved notebook metrics.
- `evaluation_outputs/run_metadata.json`: Python/scikit-learn version actually used for the recorded generation, whether it matched the project pin, and compatibility warnings.

**Version qualification:** the included generated evidence was produced in the available checking environment (Python 3.13.5 / scikit-learn 1.8.0), while the project declares Python 3.11 and scikit-learn 1.6.1. The 1N4004 notebook metrics were reproduced to displayed precision. In this diagnostic run, the recomputed GridSearchCV selected the notebook parameters and matched its recorded CV MAE; packaged SVR and RF predictions matched independently recomputed model predictions on the test rows exactly. The standard Silicon ordered metrics match to displayed precision. The SiC ordered and multi-temperature outputs show small differences from the archived notebook outputs. These are explicitly marked in the comparison CSVs. The generated outputs are useful diagnostic evidence, but they are **not claimed as an exact run under the pinned 1.6.1 environment**. Re-run with the pinned environment for strict version-matched verification.

The script is `scripts/reproduce_evaluation.py`. It refuses a version mismatch by default. For a diagnostic run only, use `--allow-version-mismatch`; metadata will record the actual runtime. Full clean-room regeneration of every saved estimator from original raw training procedures remains outside what the archived Colab notebooks support because they contain manual uploads, absolute paths and superseded cells.

## Setup and run

Python 3.11 is specified in `runtime.txt`; `requirements.txt` pins `scikit-learn==1.6.1`.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/check_environment.py
streamlit run app.py
```

To regenerate evaluation artifacts in the declared environment:

```bash
python scripts/reproduce_evaluation.py
```

The script requires scikit-learn 1.6.1 unless the diagnostic override is explicitly supplied. Run the basic physics-helper tests with:

```bash
python test_diode_physics.py
```

The `.joblib` estimators were serialized with scikit-learn 1.6.1. Keep the pinned version when loading them; loading across scikit-learn versions can produce warnings or compatibility errors.

## Limitations

1. Random splits of voltage-ordered observations can put nearby points in both train and test sets, making test performance optimistic for new voltage regions or independent measurement sessions.
2. The classified data has only two recorded temperatures (77 K and 293 K); intermediate-temperature generalization is not established.
3. Device coverage is limited to 13 devices with uneven per-device measurement counts.
4. Predictions outside measured voltage, device and temperature support are not validated.
5. The reverse-bias artifact saved by the notebook is the original untuned SVR, not the `best_svr` variable produced during tuning.
6. The notebooks are historical Colab work logs, not clean one-click training pipelines; the supplied evaluation script recreates selected evaluation designs but does not regenerate every released estimator from raw data.
7. Exact version-matched verification under scikit-learn 1.6.1 is still required for the included diagnostic outputs; see `evaluation_outputs/run_metadata.json` and `docs/ENVIRONMENT_AND_VERSION.md`.
8. No confidence intervals or independent-device validation are reported.
9. `diode_physics.py` implements an idealized Shockley utility and omits reverse breakdown, series resistance, self-heating and high-level injection. Its unit tests check equation behaviour, not experimental accuracy.
10. Historical GaN exploration exists in the notebook archive, but GaN is excluded from the active predictor and is not a supported deployed model.

## AI-use disclosure

Generative-AI assistance was used during development support and preparation of documentation, evaluation scripts, debugging and code review. The project author must review and understand every included change and adjust this disclosure if other tools or collaborators contributed. Reported notebook metrics are attributed to the included experiment notebooks; diagnostic outputs are generated by the included script and carry their runtime metadata. AI assistance is not a substitute for verifying or defending the experimental results.

## Assessment and defense documents

- `docs/ASSESSMENT_EVIDENCE.md` maps each rubric requirement to project evidence and identifies remaining qualifications.
- `docs/REPRODUCIBILITY.md` records datasets, methods, experiments and artifacts.
- `docs/LIMITATIONS_AND_FUTURE_WORK.md` explains limitations and appropriate next studies.
- `docs/INDIVIDUAL_DEFENSE.md` contains an evidence-based contribution draft, tutor questions and demonstration plan. Review personal statements for accuracy before submission.
- `docs/ENVIRONMENT_AND_VERSION.md` describes version compatibility and verification commands.
- `docs/FINAL_SUBMISSION_CHECKLIST.md` gives the final hand-in checks.

## Repository layout

```text
app.py
index.html
README.md
requirements.txt
runtime.txt
scripts/
  check_environment.py
  reproduce_evaluation.py
evaluation_outputs/
  1n4004/
  1n4004_reverse_bias/
  materials/
  run_metadata.json
data/
trained_models/
notebooks/
docs/
```
