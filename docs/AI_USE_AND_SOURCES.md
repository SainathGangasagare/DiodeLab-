# AI-use disclosure and external sources

## AI-use disclosure

Generative-AI assistance (ChatGPT) was used to support software development and code review/debugging, prepare and check documentation and evaluation-support scripts, and implement the browser-native GitHub Pages migration from the preserved Python/Streamlit application. The student remains responsible for understanding the project, reviewing the final repository, validating the results and accurately describing their individual contribution. This statement should be amended if any other AI systems, collaborators or external code sources were used. AI assistance does not replace scientific validation or the student's ability to defend the work.

Before submission, the student should review `INDIVIDUAL_DEFENSE.md` and edit its contribution statement so it lists only tasks they personally performed or clearly identifies AI-assisted, inherited, source-notebook and team contributions.

## External data sources and licenses

1. **External diode I–V sweeps:** [Diode I–V Measurements repository](https://github.com/blueberrye-io/diode-iv-measurements/). The supplied source notes identify the data as CC BY 4.0. Retain attribution and comply with the license terms when redistributing.
2. **Classified silicon and silicon-carbide measurements:** [Cryogenic and Superconducting Power Electronics Database](https://doi.org/10.57745/2AHLA6). The supplied source notes identify the data as Etalab Open License 2.0. Retain the relevant attribution and license terms.

Project-local source descriptions and license details are retained in `python-app/data/external/README.md` and `python-app/data/external/cryogenic_dataset_README.md`.

## Software and model implementation

The original Python implementation uses the packages declared in `python-app/requirements.txt`. The `.joblib` files in `python-app/` are the authoritative saved model artifacts. The GitHub Pages version is a browser-native implementation derived from those fitted estimators; it exports estimator parameters rather than retraining replacement models. The migration and validation scripts are in the repository-root `scripts/` folder.

## Browser libraries, fonts and external code references

The browser version loads the following third-party front-end dependencies from their published CDNs or hosted font service. They are dependencies used by this project; they are not model-training data or replacement estimators.

- **Plotly.js 2.35.2** provides interactive charts. See the [official Plotly.js JavaScript documentation](https://plotly.com/javascript/) and the [Plotly.js source repository and license](https://github.com/plotly/plotly.js).
- **Papa Parse 5.4.1** parses the CSV files in the browser. See the [official Papa Parse documentation](https://www.papaparse.com/docs) and [project source repository](https://github.com/mholt/PapaParse).
- **Inter** typeface and **Material Symbols Rounded** icons are loaded from [Google Fonts — Inter](https://fonts.google.com/specimen/Inter) and [Google Fonts — Material Symbols](https://fonts.google.com/icons).

No API key is required for these dependencies. The project uses their published browser distributions and documented interfaces; the DiodeLab page logic and browser-side model inference are maintained in this repository.

## Integrity note

