# DiodeLab model inventory

The active Streamlit app loads seven estimator artifacts. The notes below distinguish the inference artifacts from the archived evaluation designs.

| App label | Artifact | Inputs / target handling | Notes |
|---|---|---|---|
| Random Forest | `random_forest_model.joblib` | 1N4004 measured voltage → current (A) | 200-tree Random Forest from the 1N4004 notebook; random seed 42. |
| Tuned SVR | `tuned_svr_model.joblib` | 1N4004 measured voltage → current (A) | StandardScaler + RBF SVR; notebook grid search selected C=100, epsilon=0.0001, gamma=1. |
| Silicon SVR | `trained_models/silicon_svr.joblib` | Device, voltage and temperature → log10 current (inference returns current scale) | RBF SVR with selected C=1, epsilon=0.01; per-device voltage-ordered evaluation is documented separately. |
| SiC SVR | `trained_models/silicon_carbide_svr.joblib` | Device, voltage and temperature → log10 current (inference returns current scale) | RBF SVR with selected C=100, epsilon=0.01; per-device voltage-ordered evaluation is documented separately. |
| Silicon multi-temperature SVR | `trained_models/silicon_multi_temperature_svr.joblib` | Device, voltage and temperature → current (A) | RBF SVR with C=1, epsilon=0.01 inside a pipeline and log-target transformation. |
| SiC multi-temperature SVR | `trained_models/silicon_carbide_multi_temperature_svr.joblib` | Device, voltage and temperature → current (A) | RBF SVR with C=100, epsilon=0.01 inside a pipeline and log-target transformation. |
| 1N4004 reverse-bias SVR | `1n4004_reverse_svr_model.joblib` | Reverse voltage → log10 current (inverse-transformed by app) | The notebook's save cell stored `svr_model`, not `best_svr`; the packaged artifact is the original untuned pipeline. |

## Interpretation cautions

- The final multi-temperature model experiment is distinct from the standard per-device voltage-ordered SVR experiment. Do not merge their metrics into one table or imply they use the same split.
- `Model Comparison` shows the stored 1N4004 benchmark metrics and curve exploration for the supported material models; it does not report verified held-out Si/SiC metrics as though those were computed in the app.
- The active predictor excludes GaN even though exploratory GaN work appears in the archived expanded notebook.
- The artifacts were serialized with scikit-learn 1.6.1. Use the pinned version in `requirements.txt` when loading them.
