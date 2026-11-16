# GitHub Pages migration notes

## Source of truth

The uploaded `DiodeLab_Final_Submission_Audited(1).zip` is the source archive used for this build. It is unpacked without modifying its Python project into `python-app/`. The original Streamlit `app.py` is not edited. The original homepage from the archive remains at `python-app/index.html`; the GitHub Pages entry point is the new repository-root `index.html`.

## Interface mapping

The static site keeps the original page order, top-navigation labels, main headings, explanatory text, control names, page sections, data choices, prediction-result fields, and chart concepts from `python-app/app.py`. The dark navy/cyan theme, Inter typography, hero treatment, statistic cards, feature cards, and workflow panel are carried over from the CSS embedded in the original app. Controls that were vertically stacked in Streamlit remain vertically stacked; the original 3-column checkbox and metric/chart arrangements remain multi-column.

Pages implemented:

1. **Home** — original hero copy, four project metrics, three feature cards, workflow panel, and research note.
2. **Project Guide** — original research question, data provenance, preprocessing notes, recorded metric table, reproducibility warning, measured-device/temperature exploration, limitations, and repository note.
3. **Predictor** — original device/material choice, compatible model choices, device and measured-temperature options, unrestricted voltage entry, measured-range and polarity warnings, prediction result, interpretive disclosure, comparison checkboxes, five voltage-view modes, symmetric-log current transform, selected-voltage line, and gold prediction marker.
4. **Model Comparison** — original stored 1N4004 metrics and MAE/RMSE comparisons, plus the Silicon/SiC measured-versus-model curve workflow. The original distinction between raw log-target output for the standard material SVRs and amperes returned by the multi-temperature wrappers is preserved in the matching contexts.
5. **Dataset Explorer** — the same ten dataset choices, GaN filtering, first-500-row table, full filtered CSV download, and I–V curve when a recognized voltage/current column pair exists.

## Model execution on GitHub Pages

GitHub Pages is a static host; it does not run `app.py`, `joblib`, or Python processes. To keep predictions available without a Streamlit server, `scripts/export_browser_models.py` converts the parameters of the seven saved estimators to `assets/browser-models.json`. `assets/model-engine.js` performs inference in the browser:

- Random Forest: traverses the original saved tree structures and averages their leaf values.
- SVR: applies the stored StandardScaler values and RBF kernel over the stored support vectors, dual coefficients, intercept, and gamma.
- Material SVRs: retain the original device category order and one-hot representation, numeric feature scaling, and target conversion.

The front end keeps the original prediction routing: Random Forest and tuned SVR return amperes; the 1N4004 reverse SVR and standard material SVRs are exponentiated from log10 current in the Predictor; multi-temperature material wrappers return current in amperes. For the material Model Comparison page, the standard material SVR chart retains the original app's direct model output behavior, while multi-temperature models return amperes.

The browser JSON is a derived representation; it is not a retrained or newly fitted estimator. Keep the original `.joblib` files in `python-app/` as the authoritative saved artifacts.

## Paths

- Website entry point: `index.html`
- CSS: `assets/app.css`
- UI and page behavior: `assets/app.js`
- Browser inference: `assets/model-engine.js`
- Exported parameters: `assets/browser-models.json`
- Original Python project: `python-app/`
- Export script: `scripts/export_browser_models.py`
- Browser model parity checks: `scripts/validate_browser_models.js`

Relative paths are used so the website can be hosted in a GitHub Pages project subpath rather than requiring a domain-root deployment.
