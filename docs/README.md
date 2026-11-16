# DiodeLab submission documents

This is the **top-level documentation folder** for the GitHub Pages submission. These documents are intentionally separate from `python-app/docs/`, which is retained byte-for-byte as part of the original Python project. **Use this top-level folder as the authoritative documentation for the GitHub Pages release.** The preserved `python-app/docs/` files may describe the original pre-migration hosting arrangement.

## Start here

1. [Assessment evidence map](ASSESSMENT_EVIDENCE.md) — maps the project to the professor’s rubric and states qualifications.
2. [Reproducibility guide](REPRODUCIBILITY.md) — research question, datasets, preprocessing, model experiments, splits and metrics.
3. [Limitations and future work](LIMITATIONS_AND_FUTURE_WORK.md) — interpretation boundaries and appropriate next experiments.
4. [Individual defense preparation](INDIVIDUAL_DEFENSE.md) — technical explanations, likely questions and a demonstration plan. **Personalize the contribution section before submission.**
5. [Tutor quick start](TUTOR_QUICK_START.md) — suggested review order and reproduction commands.
6. [Final submission checklist](FINAL_SUBMISSION_CHECKLIST.md) — actions to verify before hand-in.

## Additional references

- [Model inventory](MODEL_INVENTORY.md)
- [Environment and version notes](ENVIRONMENT_AND_VERSION.md)
- [Final audit report](FINAL_AUDIT_REPORT.md)
- [AI-use disclosure and data sources](AI_USE_AND_SOURCES.md)
- [GitHub Pages migration notes](../GITHUB_PAGES_MIGRATION.md)
- [Site validation record](../SITE_VALIDATION.md)

## Where the actual project code and evidence live

The browser website is served from the repository root (`index.html`, `assets/`). The preserved original Python project is in [`python-app/README.md`](../python-app/README.md), including the original `app.py`, saved `.joblib` models, original datasets, notebooks, Python requirements, scripts, evaluation outputs, README and the original project’s own `docs/` folder.

The current GitHub Pages website is a browser-native static site. It does not execute Streamlit or Python on the server. The original Python project is preserved for inspection and local/Streamlit use.
