# DiodeLab — interactive diode I–V machine-learning project

DiodeLab explores measured diode current–voltage (I–V) behaviour and estimates current from measured voltage, device identity and recorded temperature within the scope of the supplied datasets.

## Live project links

- **Interactive GitHub Pages website:** https://sainathgangasagare.github.io/DiodeLab-GitHub/
- **GitHub Pages source repository:** https://github.com/SainathGangasagare/DiodeLab-GitHub
- **Original Python/Streamlit source repository:** https://github.com/SainathGangasagare/DiodeLab
- **Original Streamlit deployment:** https://diodelab.streamlit.app/

The GitHub Pages website is the browser-native interactive release in this repository. The original Python project is preserved under `python-app/`; it is not replaced or edited by the browser migration.

## Start here — assessment documents

The visible top-level [`docs/`](docs/README.md) folder contains the current explanations and evidence prepared for the course submission. Use this top-level folder as the authoritative documentation for the GitHub Pages release. The older `python-app/docs/` folder is preserved with the original Python project and may describe the pre-migration hosting arrangement:

- [Assessment evidence map](docs/ASSESSMENT_EVIDENCE.md) — maps the project evidence to the marking rubric.
- [Reproducibility guide](docs/REPRODUCIBILITY.md) — research question, datasets, preprocessing, methods, validation splits and metrics.
- [Limitations and future work](docs/LIMITATIONS_AND_FUTURE_WORK.md) — what the results do and do not establish.
- [Model inventory](docs/MODEL_INVENTORY.md) — the seven saved estimators and target handling.
- [Individual defense preparation](docs/INDIVIDUAL_DEFENSE.md) — technical answer frameworks and demonstration plan; personalize the contribution statement.
- [Tutor quick-start guide](docs/TUTOR_QUICK_START.md) — an instructor-friendly review route.
- [Final submission checklist](docs/FINAL_SUBMISSION_CHECKLIST.md) — checks to complete before hand-in.
- [AI-use disclosure and source citations](docs/AI_USE_AND_SOURCES.md).

## Research questions, prediction target and scope

1. How closely can regression models estimate the measured I–V response of a 1N4004 diode?
2. How do measured I–V curves for selected silicon and silicon-carbide power devices vary with voltage and measured temperature?

The primary prediction target is diode current in amperes (A). Inputs are measured voltage in volts (V); the material-specific models additionally use device identity and measured temperature in kelvin (K). A row in the 1N4004 dataset is one measured voltage/current pair. A row in the classified dataset is one measured point for one device at one recorded temperature. Predictions are model estimates, not new physical measurements. The evidence does not establish generalization to unseen devices, arbitrary temperatures or voltage regions outside the measured data.

## Website contents

The GitHub Pages application retains the five-page workflow from the original Streamlit project:

- **Home:** project overview, data scale and workflow.
- **Project Guide:** research question, data provenance, preprocessing, evaluation, interpretation and limitations.
- **Predictor:** browser-side predictions for the supported 1N4004, silicon and silicon-carbide model cases.
- **Model Comparison:** recorded 1N4004 metrics and measured-versus-model curve exploration for supported material models.
- **Dataset Explorer:** dataset selection, filtering, preview and CSV download.

## Code locations and architecture

| Location | Contents |
|---|---|
| `index.html` | GitHub Pages website entry point |
| `assets/app.css`, `assets/app.js` | Site styling, page layouts and browser interactions |
| `assets/model-engine.js` | Browser implementation of Random Forest and RBF-SVR inference |
| `assets/browser-models.json` | Exported parameters from the seven original saved estimators |
| `scripts/export_browser_models.py` | Exports saved Python estimator parameters for browser inference |
| `scripts/validate_browser_models.js` | Runs browser-engine model validation fixtures |
| `python-app/app.py` | Original Streamlit application; preserved unchanged |
| `python-app/*.joblib`, `python-app/trained_models/` | Original saved model files |
| `python-app/data/`, `python-app/*.csv` | Original source and processed datasets |
| `python-app/notebooks/` | Original experiment notebooks and notebook guide |
| `python-app/scripts/` | Python environment and evaluation scripts |
| `python-app/evaluation_outputs/` | Split manifests, metrics, predictions, residuals, plots and run metadata |
| `python-app/docs/` | Original project documentation retained with the Python source |
| `docs/` | Top-level tutor-facing assessment and submission documents |

## Dataset access and provenance

The main datasets are preserved under `python-app/`:

| File | Meaning | Rows |
|---|---|---:|
| `python-app/diode_iv_data.csv` | Cleaned 1N4004 measured voltage/current pairs | 170 |
| `python-app/data/processed/classified_diode_measurements.csv` | Silicon and SiC measurements across 13 devices | 720 |
| `python-app/data/processed/external_iv_measurements_review.csv` | Reviewed external measurements for 1N4004, 1N5229B and SB560 | 533 |
| `python-app/data/external/cryogenic_diode_measurements.csv` | Source cryogenic measurement collection | 4,201 |

The classified dataset contains 492 silicon rows and 228 silicon-carbide rows, across 9 silicon devices and 4 SiC devices, with observations at 77 K and 293 K. The external review CSV is available for exploration; it is not the active material-model training table.

Data attribution and source licenses are documented in `python-app/data/external/README.md` and `python-app/data/external/cryogenic_dataset_README.md`. The external diode I–V sweeps are attributed to the [Diode I–V Measurements repository](https://github.com/blueberrye-io/diode-iv-measurements/) (source notes identify CC BY 4.0). The classified silicon/SiC measurements are attributed to the [Cryogenic and Superconducting Power Electronics Database](https://doi.org/10.57745/2AHLA6) (source notes identify Etalab Open License 2.0). Preserve attribution and comply with the source licenses when redistributing data.

## Model and evaluation summary

Seven original saved estimators are retained: 1N4004 Random Forest, 1N4004 tuned SVR, 1N4004 reverse-bias SVR, standard Silicon SVR, standard SiC SVR, Silicon multi-temperature SVR and SiC multi-temperature SVR. The Python `.joblib` files are the authoritative saved artifacts. The browser JSON is a derived export, not a separately trained or newly fitted model.

The 1N4004 random-holdout notebook reports RF MAE 0.0001714702 A, RMSE 0.0004224828 A, R² 0.9989055; tuned SVR MAE 0.0002631377 A, RMSE 0.0003458506 A, R² 0.9992665. RF has lower MAE, while tuned SVR has lower RMSE and higher R². The much weaker voltage-ordered validation result shows why random-split scores should not be presented as proof of performance in later voltage regions or on unseen devices. Full split designs, result tables, residual evidence and interpretation are in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) and `python-app/evaluation_outputs/`.

## Running the website locally

The site requires HTTP rather than opening `index.html` directly with a `file://` URL. From the repository root run:

```bash
python -m http.server 8000
```

Open `http://127.0.0.1:8000/`. Plotly, Papa Parse, Inter and Material Symbols are loaded from fixed CDN URLs, so the interactive charts and hosted fonts/icons require an internet connection.

## Running the original Python project

The original application is under `python-app/`. It declares Python 3.11 and scikit-learn 1.6.1. From the repository root:

```bash
cd python-app
python -m venv .venv
# Activate .venv using the command for your operating system
python -m pip install -r requirements.txt
python scripts/check_environment.py
streamlit run app.py
```

The evaluation script can be run in the same pinned environment with `python scripts/reproduce_evaluation.py`. It recreates selected documented evaluation designs and outputs; it is not a clean-room pipeline that retrains every released estimator from raw measurements.

## Why the GitHub Pages version uses JavaScript

GitHub Pages serves static files and cannot execute Streamlit/Python or load `.joblib` objects directly. The migration exports the parameters of the seven original estimators into `assets/browser-models.json`. `assets/model-engine.js` implements the corresponding Random Forest tree traversal and RBF-SVR kernel calculations, including the model preprocessing and target conversions. `SITE_VALIDATION.md` records the parity test against the loaded Python estimators: 215 test inputs, zero failures, with maximum relative current difference approximately 5.6×10⁻¹¹ in the available validation environment.

The comparison validates the browser inference calculations on the tested inputs. It is distinct from the manual website acceptance check: open the deployed site in a browser and test all five pages, predictions, charts, dataset filtering and CSV downloads. See [`SITE_VALIDATION.md`](SITE_VALIDATION.md) for the validation scope.

## AI-use disclosure

Generative-AI assistance (ChatGPT) was used for development support, code review/debugging, preparation and checking of documentation and evaluation-support scripts, and the browser-native GitHub Pages migration. The project author must review and understand the final code and all submitted claims, and must adjust this disclosure if other AI tools, collaborators or sources contributed. AI assistance does not establish experimental validity and is not a substitute for personally understanding or defending the modelling decisions and results. The individual-contribution statement in `docs/INDIVIDUAL_DEFENSE.md` must be edited so it accurately describes the student's own work.

## Reproducibility and known limitations

The included evaluation outputs were generated in an available diagnostic runtime of Python 3.13.5 / scikit-learn 1.8.0; the project pins Python 3.11 / scikit-learn 1.6.1. Some SiC values differ slightly from archived notebook outputs. The evaluation script refuses a version mismatch unless an explicit diagnostic override is supplied. Run it in the declared environment before claiming strict version-matched reproduction. Other limitations include correlation among nearby points within voltage sweeps, only two recorded material temperatures, limited device coverage, no independent-device holdout, no calibrated uncertainty intervals, and historical notebooks that are not clean one-click training pipelines. The reverse-bias saved artifact is the original untuned SVR pipeline. Full details are in `docs/LIMITATIONS_AND_FUTURE_WORK.md`, `docs/ENVIRONMENT_AND_VERSION.md` and `docs/REPRODUCIBILITY.md`.
