# Site and source validation record

## Source archive

The source archive was checked before building the static site:

- ZIP integrity test: passed (no corrupt member detected).
- Archive contents: 72 entries, approximately 7.12 MB uncompressed.
- `SHA256SUMS.txt`: all 71 listed source-file hashes matched.
- The complete original project was extracted under `python-app/`.
- `python-app/app.py` is byte-for-byte identical to the uploaded archive's `app.py`.
- The original Streamlit `requirements.txt`, `runtime.txt`, `index.html`, saved `.joblib` models, CSV datasets, notebooks, docs, and evaluation outputs are retained under `python-app/`.

## Browser model verification

A browser inference representation was built for all seven saved estimators. The generated model JSON records its export environment. The JavaScript engine was compared with predictions from the loaded Python estimators using 215 inputs covering:

- 1N4004 Random Forest and tuned SVR across 25 forward-voltage samples each.
- 1N4004 reverse-bias SVR across nine reverse-voltage samples.
- Standard and multi-temperature Silicon SVRs across all Silicon devices, available measured temperatures, and three voltages per device/temperature.
- Standard and multi-temperature SiC SVRs across all SiC devices, available measured temperatures, and three voltages per device/temperature.

Recorded parity result from this build environment:

```text
cases: 215
max absolute raw-output difference: 3.602451670303708e-12
max relative current difference: 5.5570936398976144e-11
failures: 0
```

The fixture inputs and expected Python outputs are stored in `evaluation_outputs/browser_model_parity_fixtures.json`. Run `node scripts/validate_browser_models.js` from the repository root to repeat the JavaScript-side comparison.

## Important environment qualification

The saved model artifacts are documented as serialized with **Python 3.11 / scikit-learn 1.6.1**. The inspection container used for this migration had **Python 3.13.5 / scikit-learn 1.8.0** and did not have Streamlit installed. Four material-model files required a compatibility shim for a private scikit-learn pickle helper that is not present in 1.8.0; the exporter includes that shim only when needed. All seven estimators loaded for the parity comparison in this environment, but this is not a version-matched reproduction under the project's pinned 1.6.1 environment. Re-run the export and verification in Python 3.11 with scikit-learn 1.6.1 for version-matched sign-off.

## Python source checks

- `app.py`, `diode_physics.py`, `prepare_external_data.py`, and `scripts/reproduce_evaluation.py` passed Python bytecode compilation.
- `python-app/test_diode_physics.py` passed when run directly; it checks sign, zero-bias, vector output shape, finite outputs, and invalid temperature handling.
- `scripts/check_environment.py` correctly reports the inspection container's Python/scikit-learn version mismatch.
- Streamlit itself was not installed in the inspection container, so a local live Streamlit process could not be launched here. The source archive's own `requirements.txt` includes Streamlit.

## Static site checks and limitation

- JavaScript syntax checks passed for `assets/app.js` and `assets/model-engine.js`.
- The static HTML has 61 unique IDs; every statically referenced element ID exists. Five additional IDs are created dynamically for graph controls and prediction detail text.
- A headless Chromium binary was present but could not start even for a blank page in this environment. Therefore a full browser screenshot/interaction pass was not possible here. Test the hosted preview in a normal browser before submitting the Pages URL.
- Plotly, Papa Parse, Inter, and Material Symbols are loaded from fixed CDN URLs, so users need internet access for the charts and hosted fonts/icons.
