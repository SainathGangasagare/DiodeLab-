# DiodeLab — tutor quick-start guide

## Public links

- **Interactive GitHub Pages website:** https://sainathgangasagare.github.io/DiodeLab-GitHub/
- **New GitHub Pages source repository:** https://github.com/SainathGangasagare/DiodeLab-GitHub
- **Original Python/Streamlit project repository:** https://github.com/SainathGangasagare/DiodeLab
- **Original Streamlit deployment:** https://diodelab.streamlit.app/

The new GitHub Pages build is the browser-native interactive version. The original Python project is preserved in the `python-app/` subfolder of the Pages repository and in its original repository. GitHub Pages does not execute Python; its predictor uses exported parameters from the same seven saved estimators.

## Suggested review order

1. Read the root `README.md` for the research question, live website, code locations, dataset inventory, setup and AI-use disclosure.
2. Open the GitHub Pages website and try Predictor, Model Comparison and Dataset Explorer.
3. Read `docs/ASSESSMENT_EVIDENCE.md` for the rubric-to-evidence map.
4. Read `docs/REPRODUCIBILITY.md` for data preparation, model methods, split designs, metrics and experiment boundaries.
5. Inspect `python-app/evaluation_outputs/README.md`, then a split manifest, a row-level prediction/residual CSV and a residual plot.
6. Read `docs/LIMITATIONS_AND_FUTURE_WORK.md` and `docs/INDIVIDUAL_DEFENSE.md` for limitations and defense preparation. The individual contribution draft must be personalized by the student.
7. Read `SITE_VALIDATION.md` for the model parity and technical checks, including their environment and browser-test limitations.

## Reproduction commands

The original Python project is under `python-app/`. From that directory, create a Python 3.11 environment and install the project requirements:

```bash
cd python-app
python -m venv .venv
# Activate .venv using the command for your operating system
python -m pip install -r requirements.txt
python scripts/check_environment.py
python scripts/reproduce_evaluation.py
```

The original Python application and its evaluation scripts are preserved under `python-app/`. The GitHub Pages website itself runs in the browser and does not require a Python runtime.

## Interpretation cautions

- Do not interpret random-split and voltage-ordered scores as estimates of the same generalization task.
- The reverse-bias saved artifact is the original untuned SVR pipeline.
- The active models support the device families named in the application; historical GaN notebook work is exploratory and excluded from the active predictor.
- Residual outputs cover only the specific observations and model workflows stated in their folder guide.
- A 215-input browser-versus-Python parity test passed, but it does not establish accuracy on unseen devices or conditions, and it is not a visual browser acceptance test.
