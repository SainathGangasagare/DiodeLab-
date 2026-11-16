# DiodeLab — final submission checklist

Use this checklist before handing the project to the tutor. A checked box should mean you personally verified it.

## Repository and files

- [ ] Public GitHub repository is accessible to the instructor.
- [ ] Root `README.md` explains the project, code locations, datasets, setup, attribution, AI use and deployment.
- [ ] Top-level `docs/` folder is visible in the GitHub repository and contains the rubric map, reproducibility guide, limitations, model inventory, defense notes and checklist.
- [ ] Original Python project is retained in `python-app/`, including `app.py`, saved `.joblib` files, datasets, notebooks, requirements, scripts, evaluation outputs and its original documentation.
- [ ] Browser website files are present at root: `index.html`, `assets/`, browser model JSON and supporting scripts.
- [ ] Original Python project checksum manifest is present at `python-app/SHA256SUMS.txt`; its listed file hashes are verified against the preserved source files.

## Live GitHub Pages website

- [ ] Open the published Pages URL in a private/incognito window and verify it loads: https://sainathgangasagare.github.io/DiodeLab-GitHub/
- [ ] Test Home, Project Guide, Predictor, Model Comparison and Dataset Explorer.
- [ ] Test at least one forward-bias 1N4004 prediction and one supported material-model prediction.
- [ ] Check voltage and temperature controls, model selection, warnings and displayed units.
- [ ] Check I–V plots, model-comparison views, dataset table preview, filters and CSV download.
- [ ] Check the site on a desktop and a phone-sized viewport.
- [ ] Ensure GitHub Pages is configured to deploy branch `main`, folder `/(root)`.

## Machine-learning evidence and interpretation

- [ ] Research question, prediction target and units are explicit.
- [ ] Data row meaning, dataset sizes, measurement conditions, source provenance and licenses are explained.
- [ ] Preprocessing, positive-current restrictions for log-current models and train-only fitting of learned transformations are explained.
- [ ] Baseline models and nonlinear model choices are justified.
- [ ] Random and voltage-ordered evaluation designs are distinguished; do not present their scores as interchangeable.
- [ ] MAE, RMSE and R² are interpreted in context.
- [ ] Split manifests, per-row predictions/residuals, metric tables and residual plots are described only for the experiments actually represented.
- [ ] The reverse-bias saved artifact is accurately described as the original untuned SVR.
- [ ] Limitations are stated: correlated sweep points, limited device/temperature coverage, lack of independent-device validation, no uncertainty intervals, and incomplete clean-room retraining.

## Individual understanding and defense

- [ ] Edit `docs/INDIVIDUAL_DEFENSE.md` so the contribution statement is truthful and specific to your own work.
- [ ] Be able to identify which code, models, data cleaning, evaluation and documentation tasks you personally completed, and which were assisted or inherited.
- [ ] Explain Random Forest versus SVR, MAE versus RMSE, preprocessing leakage prevention, and random versus voltage-ordered splits.
- [ ] Demonstrate a prediction and explain one limitation without reading a prepared answer.
- [ ] Disclose AI assistance and external data sources accurately.

## AI disclosure and sources

- [ ] Review `docs/AI_USE_AND_SOURCES.md` and confirm it accurately describes the assistance and sources used.
- [ ] Retain the CC BY 4.0 and Etalab Open License 2.0 attribution notes when redistributing source datasets.

## Model and website verification

The browser inference engine was compared with the loaded Python estimators on 215 test inputs, with zero reported parity failures. This validates the tested model inputs; it does not replace a manual check of the deployed website. Open the live Pages URL in a private browser window and test the full interaction flow before submission.
