# DiodeLab — final submission checklist

## Repository and files

- [ ] Public repository opens for the instructor.
- [ ] Root README includes project scope, setup, data attribution, AI disclosure and both live links.
- [ ] Original notebooks, datasets, model artifacts, helper code and requirements are present.
- [ ] `docs/` contains assessment evidence, reproducibility, limitations, environment notes, model inventory, final audit and defense preparation.
- [ ] `scripts/check_environment.py` and `scripts/reproduce_evaluation.py` are present.
- [ ] `evaluation_outputs/` contains split manifests, metrics, row-level residual tables, plots and run metadata.
- [ ] `SHA256SUMS.txt` verifies against the delivered files.

## Live application

- [ ] GitHub Pages landing page opens: https://sainathgangasagare.github.io/DiodeLab/
- [ ] Streamlit application opens: https://diodelab.streamlit.app/
- [ ] Predictor works for supported device/model/temperature choices.
- [ ] Model Comparison opens and its displayed metrics have an explanation.
- [ ] Dataset Explorer loads and previews the supplied data.
- [ ] Interactive I–V graphs render.
- [ ] GaN is not presented as an active supported model.
- [ ] The instructor is told that GitHub Pages is the landing page and Streamlit currently hosts the full interactive Python app.

## ML evidence and integrity

- [ ] Research question, target and units are explicit.
- [ ] Data row meaning, sources, sizes, variables, conditions and quality cautions are explained.
- [ ] Transformations and train-only fitting of learned preprocessing are explained.
- [ ] Baselines and model choices are justified.
- [ ] Random and voltage-ordered split designs are distinguished.
- [ ] MAE, RMSE and R² are interpreted in context.
- [ ] Row-level residuals are described only for the experiments actually represented in `evaluation_outputs/`.
- [ ] `evaluation_outputs/run_metadata.json` is read and the generated diagnostic version is disclosed.
- [ ] For strict reproduction, run `python scripts/check_environment.py` and `python scripts/reproduce_evaluation.py` in Python 3.11 / scikit-learn 1.6.1. Do not mark this complete until it passes in that environment.
- [ ] The reverse-bias saved artifact is described as untuned.
- [ ] Limitations are stated, including correlated points, device/temperature coverage and no independent-device validation.

## Individual defense

- [ ] The contribution statement is personalized and truthful.
- [ ] I can explain my own code/model/data contribution.
- [ ] I can explain RF vs SVR and MAE vs RMSE.
- [ ] I can explain leakage prevention and the difference between random and voltage-ordered splits.
- [ ] I can demonstrate at least one useful interaction.
- [ ] I can discuss a limitation and propose a suitable follow-up experiment.
- [ ] AI assistance and external sources are disclosed accurately.

## Important status note

The package contains extensive evaluation outputs generated in a diagnostic environment (Python 3.13.5 / scikit-learn 1.8.0). The project is pinned to Python 3.11 / scikit-learn 1.6.1. A version-matched rerun is still required before describing all outputs as strictly reproduced. The current websites are separate: GitHub Pages is a static landing page; Streamlit hosts the interactive Python app.
