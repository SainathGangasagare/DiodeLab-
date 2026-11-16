# DiodeLab — limitations and future work

A limitation defines the conditions under which the current evidence supports a conclusion. The following points should be communicated openly in the report and tutor defense.

## Current scientific limitations

1. **Correlation within measured sweeps.** Randomly splitting a single I–V sweep can place nearby voltage observations in both training and test sets. Such points may be correlated, so random-holdout scores can be optimistic for a new voltage region or an independent measurement session. The project therefore also reports voltage-ordered validation/testing experiments.
2. **Different split designs answer different questions.** The 1N4004 random test, its first-60%/next-20% voltage-ordered validation, the per-device voltage-ordered Si/SiC SVR test, and the random multi-temperature material split are distinct experiments. Their scores should not be ranked as if they came from the same test distribution.
3. **Limited temperature coverage.** The classified material dataset contains only 77 K and 293 K measurements. The project does not establish model accuracy at intermediate temperatures.
4. **Limited device coverage.** There are 13 classified devices (9 Silicon and 4 SiC), with uneven observation counts. Performance on unseen devices is not established.
5. **Extrapolation is unvalidated.** Predictions outside the measured voltage range, device identities and recorded temperatures are not supported by the current validation evidence.
6. **Residual samples have different sizes.** Residual exports are included for selected evaluations, but some are small (for example, reverse bias has only eight test rows). Small test sets give uncertain estimates of tail error and should not be treated as broad reliability evidence.
7. **No uncertainty intervals.** The project reports point estimates and conventional error metrics; it does not provide calibrated prediction intervals or confidence intervals for generalization performance.
9. **Notebook archive is not a clean-room pipeline.** Original Colab notebooks are included, but contain manual upload/download operations, absolute paths, repeated/superseded cells and notebook state. The repository-relative evaluation script recreates selected evaluation designs and outputs; it does not regenerate every released estimator from raw data.
10. **Reverse-bias saved artifact is untuned.** In the notebook, tuning results are assigned to `best_svr`, but the final save cell serializes `svr_model`. The reverse-bias residual evidence therefore evaluates the packaged original SVR pipeline. It must not be described as the tuned model.
11. **Idealized physics helper.** `python-app/diode_physics.py` implements an idealized Shockley relation and omits reverse breakdown, series resistance, self-heating and high-level injection. Its tests validate expected equation behavior, not predictive accuracy against laboratory measurements.
12. **GaN is outside released scope.** The archived notebook includes exploratory GaN analysis and a historical fit, but GaN is not supported by the active released predictor. It should be described as exploratory/excluded, not as one of the released models.

## Error-analysis evidence now included

The `python-app/evaluation_outputs/` folder includes paired actual/predicted values, signed residuals (`actual - predicted`), absolute errors, split manifests, metric tables and residual-versus-voltage plots for the following specific evaluations:

- 1N4004 random-holdout models (RF, tuned SVR, Linear Regression and mean baseline).
- 1N4004 voltage-ordered validation models (RF, Linear Regression and mean baseline).
- Reverse-bias SVR on the eight selected test rows, using the packaged original untuned artifact.
- Standard Silicon and SiC SVR using per-device voltage-ordered outer test regions.
- Final multi-temperature Silicon and SiC SVR using the notebook's 80/20 random split.

These files provide genuine outputs from the included reproduction script. They do not eliminate the sample-size, split-design or version limitations above. Inspect each folder's CSV files and `python-app/evaluation_outputs/run_metadata.json` before interpreting results.

## Future work

- Perform grouped validation on entirely held-out devices and, where possible, independent measurement sessions.
- Expand device and temperature coverage, then evaluate intermediate temperatures using genuinely measured data.
- Preserve raw source IDs, exact split assignments and test predictions for every final training run.
- Report residual quantiles, worst-case examples and uncertainty intervals with an appropriate validation design.
- Refactor archived notebook training procedures into clean repository-relative training pipelines that regenerate the released artifacts from raw data.
- Correct and retrain the reverse-bias tuned estimator only if a tuned reverse-bias model is intended for release; otherwise retain the explicit untuned label.
- Compare physics-informed or hybrid models against the empirical baselines using independent data and non-ideal diode effects where appropriate.

## How to explain this to the tutor

State the measured scope, the evaluation design, what each result tests, and what it does not establish. A lower random-split error does not prove performance on unseen voltage regions or devices. The project is stronger when it distinguishes verified findings from diagnostic runs and future experiments rather than overstating accuracy.
