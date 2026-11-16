# DiodeLab — tutor quick-start guide

## Public links

- Project landing page: https://sainathgangasagare.github.io/DiodeLab/
- Full interactive application: https://diodelab.streamlit.app/
- Source repository: https://github.com/SainathGangasagare/DiodeLab

The Pages URL is the static project-information page. The full interactive Python app is hosted on Streamlit. These are two links for one project; the app is not executed by GitHub Pages in this release.

## Suggested review order

1. Read the root `README.md` for the research question, target/units, dataset inventory, links and setup.
2. Open the interactive app and explore Predictor, Model Comparison and Dataset Explorer.
3. Read `docs/ASSESSMENT_EVIDENCE.md` for the rubric mapping.
4. Read `docs/REPRODUCIBILITY.md` for the split designs, model methods, metrics and experiment boundaries.
5. Inspect `evaluation_outputs/README.md`, then a selected split manifest, prediction/residual CSV and residual plot.
6. Read `docs/LIMITATIONS_AND_FUTURE_WORK.md` and `docs/INDIVIDUAL_DEFENSE.md` for scientific limitations and the student's defense preparation.

## Reproduction commands

The repository declares Python 3.11 and scikit-learn 1.6.1:

```bash
python -m pip install -r requirements.txt
python scripts/check_environment.py
python scripts/reproduce_evaluation.py
```

The evaluation script checks the scikit-learn pin and refuses a mismatch unless the user explicitly requests a diagnostic run. The current packaged evaluation output metadata identifies the audit runtime as Python 3.13.5 / scikit-learn 1.8.0; a strict version-matched rerun is still required.

## Interpretation cautions

- Do not read random-split and voltage-ordered scores as directly comparable estimates of the same deployment question.
- The reverse-bias artifact is the original untuned SVR pipeline.
- The active predictor supports the listed 1N4004, Silicon and SiC models; historical GaN notebook work is exploratory and excluded.
- The residual outputs cover the specific rows and model workflows stated in their folder/readme, not every conceivable device or condition.
