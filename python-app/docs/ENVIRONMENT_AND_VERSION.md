# DiodeLab runtime and scikit-learn version

## Declared project environment

- `runtime.txt` specifies `python-3.11`.
- `requirements.txt` pins `scikit-learn==1.6.1`.
- The saved scikit-learn `.joblib` artifacts were serialized with scikit-learn 1.6.1, as recorded in the project notes.

## Why a version difference in another environment is not a website failure

The deployed Streamlit runtime and a separate local/analysis runtime are different environments. A successful Streamlit deployment indicates that the deployment's installed environment can run the application; it does not prove that an unrelated environment can load the same serialized models or exactly reproduce the notebook metrics.

The evaluation artifacts currently in this repository were generated during the audit using Python 3.13.5 and scikit-learn 1.8.0. The checker environment could not retrieve Python 3.11/scikit-learn 1.6.1 because network access was unavailable. The mismatch is recorded in `evaluation_outputs/run_metadata.json`. Some notebook comparisons match to displayed precision and some SiC values differ slightly. Treat these outputs as diagnostic until regenerated under the declared environment.

## Verify in the declared environment

From the repository root, create a Python 3.11 virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/check_environment.py
```

Expected output includes Python 3.11.x and scikit-learn 1.6.1. Then regenerate the evaluation evidence:

```bash
python scripts/reproduce_evaluation.py
```

The script refuses a scikit-learn version mismatch by default. It writes split manifests, metrics, row-level prediction/residual CSVs, residual plots and a new `evaluation_outputs/run_metadata.json`.

For diagnostic use in another version only:

```bash
python scripts/reproduce_evaluation.py --allow-version-mismatch
```

This option is not a way to claim version-matched reproduction. Leave the metadata that identifies the actual runtime in place.

## Scope and limits

This evaluation script recreates selected evaluation designs and artifacts from the archived notebooks. It does not recreate every original training process or prove that all saved model files were retrained from scratch. The notebooks are historical Colab logs with manual uploads, absolute paths and superseded cells. See `notebooks/README.md` and `docs/REPRODUCIBILITY.md`.
