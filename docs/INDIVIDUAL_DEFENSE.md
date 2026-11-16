# DiodeLab — individual defense preparation

This document provides a draft contribution statement and likely tutor questions. Review it before submission and edit anything that does not match your exact personal work or team responsibilities. You should be able to explain every statement without relying on memorized wording.

## 1. Individual contribution — draft based on the project work

My contribution to DiodeLab was to bring the diode I–V machine-learning work into a usable, documented and publicly accessible project. I maintained the project files and organized the repository so that the application, datasets, trained model artifacts, archived notebooks, helper code and supporting documentation could be reviewed together.

I worked on the user-facing application and its presentation. The original Streamlit application brought together the supported diode predictors, model comparison, dataset exploration and interactive I–V visualizations. The current GitHub Pages release ports those five areas to a browser-native interface. The original Python source and saved models are preserved in `python-app/`; the browser inference layer is derived from the seven saved estimators. Confirm and edit this paragraph to distinguish your own work from work performed with AI assistance or other contributors.

For the machine-learning evidence, I reviewed the original experiment notebooks and documented the research question, observation units, data sources, preprocessing, baselines, model configurations, evaluation split designs, reported metrics and limitations. I also prepared repository-relative evaluation and error-analysis support so that split membership, test predictions, residuals, metrics and residual plots can be inspected rather than relying only on aggregate scores. The evaluation records distinguish the notebook's random and voltage-ordered experiments and include split records, metrics and row-level error evidence.

I learned that a high random-holdout score on one measured I–V sweep does not necessarily mean that a model can predict a later voltage region or an unseen device. I also learned why preprocessing must be fitted using training data only, why MAE and RMSE can rank models differently, and why version consistency matters when loading serialized scikit-learn estimators.

**Personal verification before submission:** Confirm that the description above accurately reflects your own role. In particular, edit it to name the exact code, model-training, data-cleaning and evaluation tasks you personally performed, and identify work completed with teammates, source notebooks, external contributors or AI assistance. Do not claim that you independently trained every model unless that is true.

## 2. Key technical facts to know

- Prediction target: current in amperes (A).
- 1N4004 inputs: measured voltage in volts (V).
- Material-model inputs: device identity, measured voltage and measured temperature in kelvin (K).
- Active classified data: 720 rows across 13 devices, with 77 K and 293 K observations.
- 1N4004 random split: 102 training, 34 validation and 34 test rows (`random_state=42`).
- 1N4004 tuned SVR: RBF kernel, three-fold GridSearchCV; selected C=100, epsilon=0.0001, gamma=1.
- 1N4004: Random Forest has the lower recorded MAE; tuned SVR has the lower recorded RMSE and higher R².
- Standard material SVR: per-device voltage-ordered split; Silicon uses C=1, epsilon=0.01; SiC uses C=100, epsilon=0.01.
- Final multi-temperature models use a random 80/20 split (`random_state=42`), a fitted preprocessing pipeline and a log-current target transformation.
- The saved reverse-bias artifact is the original untuned SVR pipeline, not the tuned variable from the notebook.

## 3. Likely tutor questions and answer frameworks

### Q1. What exactly are you predicting?
The target is diode current in amperes. For the 1N4004 model, the input is measured voltage. For the material-specific models, the inputs also include device identity and recorded temperature. The model estimates current for the supported dataset scope; it does not make a new physical measurement.

### Q2. Why use Random Forest and SVR?
They are nonlinear regression methods that can represent curved I–V relationships. The 1N4004 experiment also compares them with simpler Linear Regression and a mean baseline. The comparison shows whether the nonlinear methods provide useful improvement over simple references.

### Q3. Why are MAE and RMSE both reported?
MAE is the average absolute difference between prediction and measurement, in amperes. RMSE also uses squared errors and penalizes larger misses more strongly. In the recorded 1N4004 test, RF has lower MAE while tuned SVR has lower RMSE and higher R², so the preferred model depends on which error characteristic matters.

### Q4. Why might a random split overestimate performance on a measured I–V curve?
Adjacent voltage/current observations from one sweep may be correlated. A random split can put neighboring points in both training and test sets, making the test points easier than a genuinely later voltage region. The voltage-ordered experiment tests that different situation and has substantially weaker performance for 1N4004.

### Q5. How did you avoid preprocessing leakage?
For the material models, scaling and one-hot encoding are inside a scikit-learn pipeline. The pipeline is fitted on the training partition, so the held-out test rows do not determine the fitted scaler or encoder. The split is made before fitting the preprocessing pipeline.

### Q6. Why are only 77 K and 293 K available?
Those are the measured temperatures represented in the active classified dataset. The project does not have measured evidence for intermediate temperatures, so it does not present those as validated conditions.

### Q7. What is one major limitation?
A major limitation is the possibility of correlated measurements in random splits, alongside limited device and temperature coverage. An appropriate next study would hold out complete devices or independent measurement sessions and report performance on that genuinely unseen data.

### Q8. Why does GitHub Pages use JavaScript when the original project uses Python?
GitHub Pages is a static host and cannot execute Streamlit or Python. The browser version uses JavaScript for the interface and inference, with estimator parameters exported from the seven saved Python models. The original Python project remains preserved under `python-app/`. The browser model engine was compared with the loaded Python estimators on 215 test inputs, with zero reported parity failures.

### Q9. Is the reverse-bias model tuned?
The notebook creates a tuned variable called `best_svr`, but its final save cell saves `svr_model`, the original untuned pipeline. The packaged reverse-bias artifact is therefore described as untuned. This is a technical integrity point, not something to conceal.

### Q10. What would you change to test generalization better?
I would use grouped validation by device or measurement session, hold out complete devices for testing, preserve exact split IDs, and report per-row errors and uncertainty. I would also collect more devices and measured temperatures before making broader claims.

### Q11. Does a high R² mean the model is accurate everywhere?
No. R² summarizes performance on a specific test set and target scale. It does not prove accuracy outside the test distribution or on other devices, temperatures or measurement sessions. MAE/RMSE and residual inspection are needed alongside it.

### Q12. What does the browser model validation establish?
The documented 215-input comparison checks that the browser inference engine reproduces outputs from the loaded Python estimators on the selected test inputs. It does not by itself prove generalization beyond the measured data or replace manually testing the website interactions.

## 4. Five-minute demonstration plan

1. State the research question, prediction target and units.
2. Show the datasets and explain what one row represents.
3. Demonstrate a prediction for a supported device and measured condition.
4. Show the recorded model comparison and explain MAE versus RMSE.
5. Explore one dataset and one interactive I–V plot.
6. Show the evaluation evidence under `python-app/evaluation_outputs/`: a split manifest, a row-level prediction/residual CSV and a residual plot. Then show the browser parity result in `SITE_VALIDATION.md`.
7. Explain one limitation and describe a specific experiment that would address it.

## 5. Small-change reasoning exercise

If the tutor asks what happens when the split changes from random to voltage-ordered, explain that the evaluation question changes. A random split tests interpolation among randomly selected points from the same sweep; a voltage-ordered split tests performance on a later voltage segment not represented in training. The score may fall because the latter is a harder extrapolation-like task. That change does not automatically mean the code is broken.

## 6. Final personal checks

- [ ] I have edited the contribution statement so every claim is true for my own role.
- [ ] I can identify what I personally coded, trained, cleaned, tested and documented.
- [ ] I understand which work was based on original notebooks or external data and which was AI-assisted.
- [ ] I can explain the 1N4004 metrics and why RF and SVR have different metric rankings.
- [ ] I can explain the difference between random and voltage-ordered evaluation.
- [ ] I can explain why GitHub Pages uses browser-side JavaScript and accurately describe the reverse-bias artifact.
- [ ] I can demonstrate the published application without relying on this document.
