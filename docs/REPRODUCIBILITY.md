# DiodeLab: data, experiments, evaluation and reproducibility

## 1. Research question, target and limits

The project asks how closely regression models estimate diode current from measured voltage for a 1N4004 diode, and how measured I–V responses of selected silicon and silicon-carbide power devices vary with voltage and measured temperature. The primary target is current in amperes (A). Inputs are voltage (V), device identity and (for material-specific workflows) temperature (K). A row represents one measured point, not an independent device.

The application is an educational predictor over the represented devices and measured conditions. Predictions are estimates, not measurements. Performance on unseen devices, independent measurement sessions, intermediate temperatures or unsupported extrapolation regions is not established.

## 2. Datasets and provenance

- `python-app/diode_iv_data.csv`: 170 cleaned 1N4004 voltage/current pairs. The source notebook begins with 171 rows and drops one pair with missing measured voltage/current.
- `python-app/data/processed/classified_diode_measurements.csv`: 720 rows across 13 devices: 492 silicon observations (9 devices) and 228 silicon-carbide observations (4 devices). Recorded temperatures are 77 K and 293 K.
- `python-app/data/processed/external_iv_measurements_review.csv`: 533 reviewed external sweep rows for 1N4004, 1N5229B and SB560.
- `python-app/data/external/cryogenic_diode_measurements.csv`: 4,201 rows in the source cryogenic collection.

External diode sweeps are attributed to the Diode I–V Measurements repository (source notes identify CC BY 4.0). Classified silicon/SiC data is attributed to the Cryogenic and Superconducting Power Electronics Database (source notes identify Etalab Open License 2.0). See `python-app/data/external/README.md` and `python-app/data/external/cryogenic_dataset_README.md`.

Variables include measured voltage (`v_meas` or `voltage_V`), measured current (`i_meas` or `current_A`), `device`, `material`, and `temperature_K`, with source/provenance fields retained in classified data.

## 3. Preprocessing

- 1N4004: retain measured voltage/current, remove rows with missing values, and sort voltage for voltage-ordered evaluation. The random experiment uses the cleaned 170-row data ordering.
- Standard material SVR: retain complete material/device/temperature/voltage/current rows, use positive-current rows for logarithmic current modelling, create per-device voltage-sorted training/test partitions, one-hot encode device, scale voltage and temperature, and fit RBF SVR on `log10_current_A`.
- Final multi-temperature material SVR: retain complete required fields and positive current rows; use features `device`, `voltage_V`, `temperature_K`; apply `StandardScaler` to numeric columns and `OneHotEncoder(handle_unknown="ignore")` to device within a `ColumnTransformer`; wrap RBF SVR in `TransformedTargetRegressor` with `log10` and named inverse `inverse_log_current`.
- Reverse bias: remove non-positive-current observations, sort by voltage and use eight selected positions as test rows.

For pipeline-based material models, the learned scaler/encoder is fitted only on the training region. Do not fit preprocessing on the entire dataset before splitting.

## 4. 1N4004 forward-bias experiment

`python-app/notebooks/ML_PROJECT.ipynb` records a random split that first reserves 20% for test (`random_state=42`) and then 25% of the remaining rows for validation. The displayed split is 102 train, 34 validation and 34 test rows. Random Forest uses 200 trees and `random_state=42`. SVR tuning uses a StandardScaler + RBF SVR pipeline and three-fold GridSearchCV, with:

- `C`: 1, 10, 100, 1000
- `epsilon`: 0.0001, 0.001, 0.005
- `gamma`: `scale`, 0.1, 1

The recorded best settings are C=100, epsilon=0.0001, gamma=1. The notebook's final test metrics are:

| Model | MAE (A) | RMSE (A) | R² |
|---|---:|---:|---:|
| Random Forest | 0.0001714702 | 0.0004224828 | 0.9989055 |
| Tuned SVR | 0.0002631377 | 0.0003458506 | 0.9992665 |
| Linear Regression | 0.006944 | 0.009559 | 0.439677 |
| Mean baseline | 0.008777 | 0.012815 | -0.007052 |

Random Forest has the lowest MAE; tuned SVR has the lowest RMSE and highest R². MAE and RMSE weight errors differently, so there is no single universal winner across metrics.

The evaluation script reconstructs the same 102/34/34 split, loads the packaged RF and tuned-SVR artifacts, fits the Linear Regression and mean baselines on the training partition, and exports row-level test predictions/residuals. It also reruns the three-fold GridSearchCV, exports all 36 candidate CV results and records the best parameters/CV score. In the current audit run, the search selected the notebook parameters and CV MAE; the packaged RF/SVR test predictions matched independently refitted/recomputed predictions exactly, and the displayed 1N4004 metrics were reproduced to the shown precision.

## 5. 1N4004 voltage-ordered validation

The notebook sorts the 170 cleaned rows by voltage, fits on the first 60% (102 rows) and validates on the next 20% (34 rows). The final 20% is not used in this comparison. Recorded Random Forest validation MAE is approximately 0.001267 A, RMSE 0.001781 A and R² -1.024895. The substantially weaker result than random holdout indicates that random splitting can be optimistic when adjacent points from one sweep are related. It is a validation experiment, not a reported held-out test evaluation.

The evaluation script exports this ordered split manifest, row-level validation predictions/residuals, metrics and residual plot.

## 6. Standard Silicon and SiC SVR: voltage-ordered per-device evaluation

`python-app/notebooks/FINAL_BOSS_ML.ipynb` cells 94 and 98–103 document this workflow. For each device, voltage is sorted and the first 80% of that device's measurements form the outer training region; the final 20% are held out for testing. Hyperparameter selection uses an additional per-device validation segment inside the outer training region. The grid is C in [1, 10, 100, 1000] and epsilon in [0.01, 0.05, 0.1]. The selected settings recorded by the notebook are:

- Silicon: C=1, epsilon=0.01
- Silicon carbide: C=100, epsilon=0.01

The notebook's test metrics are:

| Material | Test rows | MAE (A) | RMSE (A) |
|---|---:|---:|---:|
| Silicon | 98 | 4.432537 | 7.032687 |
| Silicon carbide | 45 | 1.389171 | 1.708090 |

The evaluation script recreates the per-device outer split, inner tuning/validation split, all 12 grid candidates' validation results, and row-level held-out predictions/residuals. The exported comparison includes per-row held-out predictions and residuals. The R² emitted by the script is a supplementary log-current-scale calculation; the cited notebook cell reports MAE and RMSE only.

The notebook's later cell 103 fits the deployable standard Silicon/SiC SVR artifacts on all positive-current rows after the evaluation settings are selected. The voltage-ordered evaluation metrics above describe the held-out method-selection evaluation, not a separately saved test-only estimator artifact.

## 7. Final multi-temperature Silicon/SiC experiment

The corrected final workflow is cell 348 (one-based) in `python-app/notebooks/FINAL_BOSS_ML.ipynb`. It removes rows with missing required fields and non-positive current, uses an 80/20 random split (`random_state=42`), fits one-hot encoding and scaling on training rows only, uses RBF SVR with C=1 for Silicon and C=100 for SiC, epsilon=0.01, and applies `log10`/inverse-log target transformation. The notebook reports:

| Material | Positive rows | Devices | Test rows | MAE (A) | RMSE (A) | R² |
|---|---:|---:|---:|---:|---:|---:|
| Silicon | 474 | 9 | 95 | 0.974620 | 2.241743 | 0.995511 |
| Silicon carbide | 220 | 4 | 44 | 0.187943 | 0.251970 | 0.998697 |

The script refits this experiment and exports exact split manifests and row-level predictions/residuals. The evaluation outputs include the split manifest, held-out predictions, residuals and a notebook-metric comparison for inspection.

A supplementary mean baseline is also calculated on the same split for assessment context. It is clearly labelled as an additional comparison, not as a metric reported by the original notebook.

## 8. Reverse-bias experiment

The reverse-bias source has 41 rows; the notebook removes three non-positive-current rows, then uses the eight sorted positions `[2, 7, 12, 17, 22, 27, 32, 37]` as test rows and the remaining 30 as training rows. The notebook's final save cell serializes `svr_model`, not the tuned variable `best_svr`; therefore the packaged artifact is described as the original untuned SVR pipeline. The evaluation script loads that packaged artifact and exports its eight row-level predictions, residuals and metrics.

## 9. Evaluation outputs and script

Run from the repository root:

```bash
python python-app/scripts/check_environment.py
python python-app/scripts/reproduce_evaluation.py
```

The evaluation script uses the dependencies declared by the original Python project. It creates/updates:

- `python-app/evaluation_outputs/1n4004/`: random and voltage-ordered split manifests, metrics, prediction/residual CSVs, residual plots and the SVR tuning configuration/record.
- `python-app/evaluation_outputs/1n4004_reverse_bias/`: reverse-bias split manifest, eight test predictions/residuals, metrics and residual plot.
- `python-app/evaluation_outputs/materials/`: multi-temperature random split manifests/predictions/metrics/plots; standard per-device voltage-ordered split and tuning manifests; grid validation table; standard material predictions/residuals/metrics/plots; notebook comparisons.
- `python-app/evaluation_outputs/run_metadata.json`: recorded evaluation-run details and interpretation notes.

The 1N4004 tuning record is written to `python-app/evaluation_outputs/1n4004/tuning_record.json`, and the candidate-level CV table is `python-app/evaluation_outputs/1n4004/grid_search_cv_results.csv`. These files preserve the candidate-level search evidence alongside the reported notebook results.

## 10. Notebook and model caveats

The two notebooks are preserved as historical Colab work logs. They contain manual upload/download steps, absolute `/content/...` paths, repeated/superseded cells and notebook-specific state. They are not clean one-click training pipelines. Use `python-app/notebooks/README.md` for experiment-cell guidance.

The expanded notebook also contains exploratory GaN analysis and an experimental fit. GaN is excluded from the released active predictor. The reverse-bias saved artifact is untuned as explained above. Do not claim all released model artifacts have been retrained from scratch by `python-app/scripts/reproduce_evaluation.py`.

## 11. Limitations

- Random holdout within a single measured sweep may overstate performance for new voltage regions or independent measurement sessions.
- Only 77 K and 293 K are represented for active material predictions.
- Device counts are limited and uneven.
- No independent-device holdout or confidence intervals are reported.
- Voltage extrapolation and intermediate-temperature predictions are not established.
- The idealized Shockley helper omits reverse breakdown, series resistance, self-heating and high-level injection; its unit tests check equation behaviour only.

## 12. Environment and AI disclosure

The original Python project records its runtime and dependencies in `python-app/runtime.txt` and `python-app/requirements.txt`. Use that project environment when running the preserved Streamlit application or inspecting its serialized estimators. AI assistance was used for development support, documentation, evaluation-script preparation, debugging and code review; the project author should verify and accurately disclose all assistance and personally performed contributions.
