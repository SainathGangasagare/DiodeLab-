# DiodeLab runtime and deployment

## GitHub Pages website

The published website is a static, browser-native application. It runs its interface and prediction engine in the visitor's browser using HTML, CSS and JavaScript. GitHub Pages serves these files directly; it does not need a Python server, Streamlit process, API key or backend service.

To run the website locally, open a terminal at the repository root and run:

```bash
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/` in a browser. An internet connection is needed for the external charting, CSV parsing, font and icon libraries loaded by the page.

## Original Python project

The original Streamlit application is preserved in `python-app/` as the source project. Its own `runtime.txt` and `requirements.txt` document the environment for running that Python application and inspecting its saved estimator files. Those Python dependencies are not required to host or use the GitHub Pages website.

From the repository root, the original application can be started with:

```bash
cd python-app
python -m venv .venv
# Activate the virtual environment for your operating system
python -m pip install -r requirements.txt
streamlit run app.py
```

## Model implementation in the browser

The seven browser models are derived from the saved estimators in the original Python project. `scripts/export_browser_models.py` creates the browser model data, and `assets/model-engine.js` performs the corresponding inference in JavaScript. The browser site does not load Python `.joblib` files at runtime.

The model-engine comparison is documented in `SITE_VALIDATION.md`: 215 test inputs were checked against the loaded Python estimators, with zero reported parity failures. This is a model-output comparison; it is distinct from manually testing every user interaction in a deployed browser.
