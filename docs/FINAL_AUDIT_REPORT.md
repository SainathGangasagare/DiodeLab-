# DiodeLab package contents and verification

This document records the project evidence and technical checks included in this repository. It is not a grade prediction.

## Evidence available for the course rubric

| Rubric area | Evidence in the repository |
|---|---|
| Problem formulation and scope | Research questions, prediction target, units, intended use and scope in the root README and reproducibility guide |
| Data understanding | Dataset inventory, row meanings, source attribution, licenses and data-quality notes in the README and source documentation |
| Preprocessing and statistical reasoning | Notebook workflows and reproducibility guide, including positive-current handling, feature encoding, scaling and train-fitted preprocessing |
| Baseline and method selection | 1N4004 baseline comparisons, Random Forest and SVR results, material-model tuning records and model inventory |
| Evaluation design and metrics | Documented train/validation/test designs, random and voltage-ordered evaluations, MAE, RMSE and R², split records and prediction/error outputs |
| Results, errors and limitations | Metric interpretation, residual evidence, random-versus-ordered comparison and limitations/future-work discussion |
| Reproducibility and technical integrity | Original notebooks, source code, data files, requirements, scripts, saved estimators, split/evaluation artifacts and checksum manifest |
| Interactive website | Five-page GitHub Pages application with Predictor, Model Comparison and Dataset Explorer |
| Useful interaction | Browser predictions, model selection, interactive I–V views, dataset preview/filtering and CSV download |
| Individual understanding and defense | Viva preparation, technical question frameworks and demonstration outline in `INDIVIDUAL_DEFENSE.md` |

## Package and integrity checks

- The uploaded Python source archive was checked before migration.
- The original Python project is preserved under `python-app/`.
- The original `python-app/app.py`, model artifacts, datasets, notebooks and project files were not edited by the website migration.
- The original checksum manifest was checked against its listed source files.
- Browser model parameters were exported from the seven saved estimators.
- The browser inference engine was compared with the loaded Python estimators over 215 inputs; the recorded comparison reports zero failures and a maximum relative current difference of approximately 5.6×10⁻¹¹.
- JavaScript syntax, Python compilation and local HTTP asset/data checks passed, as summarized in `SITE_VALIDATION.md`.
- The top-level `docs/` folder contains the tutor-facing documentation for this GitHub Pages release. The original `python-app/docs/` folder remains with the preserved Python project.

## Final checks for the student

Before submitting, open the deployed website in a private/incognito browser window and test all five pages, predictions, charts, dataset filtering and CSV download. Review the AI-use disclosure and citations. Personalize the contribution statement in `INDIVIDUAL_DEFENSE.md` so it accurately describes the work you personally completed and can explain during the viva.
