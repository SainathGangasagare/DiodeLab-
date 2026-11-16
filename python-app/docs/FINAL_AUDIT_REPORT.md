# DiodeLab final package audit

This report records the contents and checks performed on the submission package. It is an audit trail, not a grade prediction.

## Rubric coverage map

| Rubric item | Points | Evidence in this package | Status/qualification |
|---|---:|---|---|
| Problem formulation and scope | 10 | README, reproducibility guide, notebooks | Documented; scope and units explicit |
| Data understanding | 10 | README, source notes, data inventory | Data size, row meaning, variables, sources and licenses documented |
| Preprocessing and statistical reasoning | 10 | Notebooks, reproducibility guide, evaluation script | Train-fitted preprocessing documented; split-design distinctions explained |
| Baseline and method selection | 15 | 1N4004 metrics, supplementary material baseline, tuning grid | Baselines and method settings recorded; assumptions/limits explained |
| Evaluation design and metrics | 20 | Notebook records, split manifests, metrics, tuning grid and runtime metadata | Stronger row-level evidence included; strict version-matched rerun still required |
| Results, errors and limitations | 10 | Prediction/residual CSVs and plots, limitations guide | Residual evidence provided for selected experiments; small samples and mismatch disclosed |
| Reproducibility and technical integrity | 5 | Requirements, runtime, scripts, notebooks, checksums, metadata | Selected evaluations reproducible by script; not a complete raw-data retraining pipeline |
| Interactive website | 10 | GitHub Pages and Streamlit links, app and index | Published and working according to user; currently split across two URLs |
| Useful interaction | 5 | Streamlit app | Predictor, model controls, plots and dataset exploration |
| Individual understanding and defense | 5 | `docs/INDIVIDUAL_DEFENSE.md` | Draft answers and demonstration plan included; user must review personal contribution claims |

## Checks performed on the supplied project files

- ZIP contents inspected and project directory structure reviewed.
- `app.py` and Python helper/script files parsed for Python syntax.
- `scripts/reproduce_evaluation.py` run in diagnostic mode under Python 3.13.5 / scikit-learn 1.8.0.
- Evaluation manifests, metrics, predictions/residuals and plots generated for the documented workflows.
- The 1N4004 three-fold grid search was rerun; its best settings and CV MAE matched the notebook record in the diagnostic runtime. Packaged RF and tuned-SVR predictions matched the independently refitted/recomputed model predictions exactly on the reconstructed test/validation rows.
- `test_diode_physics.py` run successfully (physics-helper equation checks only).
- Existing `app.py`, `index.html`, trained model files, requirements and data files retained without editing for this documentation/evaluation package.
- File checksums regenerated for the final package.

## Important qualifications

1. The audit runtime did not match the declared Python 3.11 / scikit-learn 1.6.1 environment. The evaluation script therefore ran with an explicit diagnostic override and records this in `evaluation_outputs/run_metadata.json`.
2. Under the diagnostic runtime, the 1N4004 random metrics and standard Silicon ordered metrics match the notebook values to displayed precision. SiC standard ordered and multi-temperature results differ slightly from notebook outputs and are flagged.
3. A successful Streamlit deployment and the diagnostic runtime mismatch are separate facts. A different local version does not establish that the deployed app is broken; it does mean the current evaluation output is not strict version-matched reproduction.
4. Archived notebooks are Colab work logs, not polished one-click full training pipelines. The included script reproduces selected evaluation designs and exports row-level evidence, but it does not retrain every distributed estimator from raw data.
5. The reverse-bias saved artifact is the original untuned model, despite an earlier tuned variable in the notebook.
6. Individual contribution statements are a draft based on visible project tasks. The student must confirm and edit them for exact personal accuracy.
7. The GitHub Pages site is a static landing page; the full interactive app is hosted on Streamlit. A future browser-only GitHub Pages migration is separate from this submitted version.

## Release recommendation

The package is substantially more complete and transparent than the originally supplied ZIP. Before making a strict claim of complete reproducibility, run the environment check and evaluation script in Python 3.11 with scikit-learn 1.6.1 and review the newly generated metric comparisons. Before final hand-in, the student should personalize the defense contribution section and confirm the live links work from an instructor-accessible browser.
