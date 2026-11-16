import os
import sys
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
def inverse_log_current(x):
    return np.power(10.0, x)
st.set_page_config(
    page_title="DiodeLab | Interactive I–V Explorer",
    page_icon="diodelab_favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)



# ---------- Theme and styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at 50% -18%, rgba(0,153,255,.22), transparent 48%), radial-gradient(circle at 85% 25%, rgba(0,210,255,.08), transparent 28%), #050b18; color:#eaf4ff; }
header[data-testid="stHeader"] { height: 0.25rem; background: transparent; }
.block-container { max-width: 1320px; padding-top: .55rem !important; padding-bottom: 2.5rem; }
[data-testid="stSidebar"] { display:none; }
h1,h2,h3,h4 { color:#f3f8ff; letter-spacing:-.025em; }
p, label, .stMarkdown { color:#b9cce3; }
.hero { position:relative; overflow:hidden; padding:clamp(2rem,5vw,4.5rem); border:1px solid rgba(70,174,255,.35); border-radius:24px; background:radial-gradient(ellipse at 78% 40%,rgba(0,149,255,.22),transparent 42%),linear-gradient(115deg,#0b1830 0%,#0b2445 58%,#071326 100%); box-shadow:0 20px 70px rgba(0,80,180,.16);  }
.hero:after { content:' '; position:absolute; width:310px; height:310px; right:-85px; top:-115px; border-radius:50%; border:1px solid rgba(90,195,255,.18); box-shadow:0 0 0 28px rgba(90,195,255,.035),0 0 0 58px rgba(90,195,255,.025); pointer-events:none; }
.eyebrow { display:inline-block; padding:.4rem .75rem; border-radius:999px; border:1px solid rgba(83,190,255,.4); color:#79d8ff; background:rgba(10,100,180,.15); font-size:.72rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }
.hero h1 { color:#f4f9ff; font-size:clamp(2.3rem,5.5vw,4.4rem); line-height:1.03; margin:1rem 0; }
.gradient-text { background:linear-gradient(90deg,#55d7ff,#4b91ff,#9b8cff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero p { color:#b5cce5; font-size:1.05rem; max-width:780px; line-height:1.8; }
.metric-card,.content-card { background:linear-gradient(145deg,rgba(15,33,59,.96),rgba(8,20,39,.96)); border:1px solid #203b5d; border-radius:16px; padding:1.1rem 1.2rem; box-shadow:0 8px 24px rgba(0,0,0,.12); transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease; }
.metric-card:hover,.content-card:hover { transform:translateY(-3px); border-color:#38bdf8; box-shadow:0 12px 30px rgba(0,145,255,.12); }
.metric-label { color:#9bb5d2; font-size:.85rem; }.metric-value { color:#f2f8ff; font-size:1.75rem; font-weight:800; margin-top:.25rem; }.metric-note { color:#7995b6; font-size:.8rem; margin-top:.2rem; }
.section-kicker { color:#5bd5ff; text-transform:uppercase; font-size:.76rem; font-weight:800; letter-spacing:.14em; }.small-muted { color:#a8bfd9; font-size:.9rem; }
div.stButton > button, div[data-testid="stDownloadButton"] button { border-radius:10px; border:1px solid #168de0; background:linear-gradient(100deg,#0878db,#05a6cf); color:#fff !important; font-weight:700; padding:.72rem 1rem; transition:transform .2s ease,filter .2s ease; }
div.stButton > button p, div[data-testid="stDownloadButton"] button p { color:#fff !important; font-weight:700; }
div.stButton > button:hover,
div[data-testid="stDownloadButton"] button:hover {
    filter: brightness(1.12);
    color: #fff !important;
    border-color: #5bd5ff;
}

/* Keep button positions stable while clicking */
div.stButton > button,
div[data-testid="stDownloadButton"] button {
    transform: none !important;
    transition: filter 0.15s ease, border-color 0.15s ease;
    cursor: pointer;
}

/* Make keyboard focus visible without moving the button */
div.stButton > button:focus-visible {
    outline: 2px solid #5bd5ff;
    outline-offset: 2px;
}
[data-testid="stMetric"] { background:#0c1c33; border:1px solid #203b5d; padding:1rem; border-radius:14px; }
[data-testid="stDataFrame"] { border:1px solid #203b5d; border-radius:12px; overflow:hidden; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div { background:#0c1c33; border-color:#315274; color:#eaf4ff; }
.stSlider [data-baseweb="slider"] div { color:#eaf4ff; }
[data-testid="stAlert"] { border-radius:12px; }
@keyframes rise { from {opacity:0; transform:translateY(12px)} to {opacity:1; transform:translateY(0)} }
hr { border-color:#203b5d; }
/* Fix top navigation button click area */
div[data-testid="stHorizontalBlock"] div.stButton {
    position: relative;
    z-index: 10;
}

div[data-testid="stHorizontalBlock"] div.stButton > button {
    position: relative;
    z-index: 11;
    pointer-events: auto;
}

.brand-mark { display:inline-flex; align-items:center; justify-content:center; width:1.65rem; height:1.65rem; margin-right:.42rem; border-radius:8px; color:#061326; background:linear-gradient(135deg,#6ee7f9,#60a5fa); font-size:.95rem; font-weight:900; vertical-align:middle; box-shadow:0 4px 16px rgba(56,189,248,.25); }
.hero { animation:rise .55s ease both; }
.hero-topline { display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap; }
.hero-status { color:#b8d5ee; font-size:.78rem; font-weight:600; }
.status-dot { display:inline-block; width:7px; height:7px; margin-right:.45rem; border-radius:50%; background:#34d399; box-shadow:0 0 12px rgba(52,211,153,.8); }
.hero-actions { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.5rem; }
.hero-chip { display:inline-block; border:1px solid rgba(125,190,255,.25); border-radius:999px; padding:.42rem .75rem; color:#c7e6ff; background:rgba(12,52,91,.45); font-size:.78rem; font-weight:600; }
.section-heading { display:flex; justify-content:space-between; align-items:end; margin:.6rem 0 1rem; }
.section-heading h2,.workflow-panel h2 { margin:.25rem 0; color:#f3f8ff; font-size:1.55rem; letter-spacing:-.035em; }
.feature-card { min-height:220px; padding:1.25rem; border:1px solid #234362; border-radius:18px; background:linear-gradient(150deg,rgba(17,42,72,.96),rgba(8,20,39,.98)); transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease; }
.feature-card:hover { transform:translateY(-5px); border-color:#55c9f5; box-shadow:0 16px 34px rgba(0,145,255,.14); }
.feature-card h3 { margin:.9rem 0 .45rem; color:#f3f8ff; }
.feature-card p { min-height:3.5rem; color:#a9c1da; line-height:1.6; }
.feature-icon { display:flex; width:2.45rem; height:2.45rem; align-items:center; justify-content:center; border:1px solid rgba(91,213,255,.35); border-radius:12px; background:rgba(19,128,194,.15); color:#75dcff; font-size:.8rem; font-weight:800; }
.feature-tag { display:inline-block; margin-top:.35rem; color:#79d8ff; font-size:.72rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }
.workflow-panel { margin-top:.7rem; padding:1.5rem; border:1px solid #203b5d; border-radius:18px; background:linear-gradient(130deg,rgba(13,35,62,.95),rgba(7,18,34,.96)); }
.workflow-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1.2rem; margin-top:1.25rem; }
.workflow-grid > div { padding:1rem; border-radius:13px; background:rgba(18,47,78,.48); border:1px solid rgba(79,142,190,.2); }
.workflow-number { display:flex; align-items:center; justify-content:center; width:1.8rem; height:1.8rem; margin-bottom:.7rem; border-radius:8px; background:rgba(45,165,220,.18); color:#78ddff; font-size:.78rem; font-weight:800; }
.workflow-grid strong { display:block; color:#e8f5ff; margin-bottom:.3rem; }
.workflow-grid p { margin:0; color:#9eb8d2; font-size:.86rem; line-height:1.55; }
div[data-testid="stHorizontalBlock"] div.stButton > button { min-height:2.65rem; border-radius:11px; }
@media (max-width: 800px) { .workflow-grid { grid-template-columns:1fr; } .hero-status { display:none; } }

</style>
""", unsafe_allow_html=True)

# ---------- Load project assets ----------

@st.cache_resource
def load_models():
    loaded = {}
    errors = []

    # Make the saved function accessible to Joblib during model loading.
    sys.modules["__main__"].inverse_log_current = inverse_log_current

    for label, filename in [
        ("Random Forest", "random_forest_model.joblib"),
        ("Tuned SVR", "tuned_svr_model.joblib"),
        ("Silicon SVR", "trained_models/silicon_svr.joblib"),
        ("SiC SVR", "trained_models/silicon_carbide_svr.joblib"),
        ("Silicon multi-temperature SVR", "trained_models/silicon_multi_temperature_svr.joblib"),
        ("SiC multi-temperature SVR", "trained_models/silicon_carbide_multi_temperature_svr.joblib"),
       
        ("1N4004 Reverse-bias SVR", "1n4004_reverse_svr_model.joblib"),
    ]:

        if os.path.exists(filename):
            try:
                loaded[label] = joblib.load(filename)
            except Exception as exc:
                errors.append(f"{filename}: {exc}")
        else:
            errors.append(f"Missing file: {filename}")

    return loaded, errors


@st.cache_data
def load_data():
    path = "diode_iv_data.csv"
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    # Standardize the expected column names while preserving source values.
    if {"v_meas", "i_meas"}.issubset(df.columns):
        df = df[["v_meas", "i_meas"]].dropna().copy()
        df = df.sort_values("v_meas").reset_index(drop=True)
    return df


@st.cache_data
def load_training_data():
    path = "data/processed/classified_diode_measurements.csv"

    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)

    required_columns = {
        "device",
        "material",
        "voltage_V",
        "current_A",
        "temperature_K",
    }

    if not required_columns.issubset(df.columns):
        return pd.DataFrame()

    df = df.dropna(
        subset=["device", "voltage_V", "current_A", "temperature_K"]
    ).copy()

    # Keep the app's prediction data restricted to trained material families.
    is_gan = df["material"].astype(str).str.contains(
        r"\bgan\b|gallium nitride",
        case=False,
        regex=True,
        na=False,
    )
    df = df[~is_gan].copy()

    return df



# ---------- Discover all available measurement CSVs ----------
DATASET_FILES = {
    "1N4004 forward bias": "data/external/1n4004_forward.csv",
    "1N4004 reverse bias": "data/external/1n4004_reverse.csv",
    "1N4004 reverse bias (10 µA range)": "data/external/1n4004_reverse_10uA_range.csv",
    "1N5229B Zener reverse bias": "data/external/1n5229b_reverse.csv",
    "SB560 forward bias": "data/external/sb560_forward.csv",
    "SB560 reverse bias": "data/external/sb560_reverse.csv",
    "Cryogenic diode measurements": "data/external/cryogenic_diode_measurements.csv",
    
    "Classified combined measurements": "data/processed/classified_diode_measurements.csv",
    "External measurements review": "data/processed/external_iv_measurements_review.csv",
    "Original cleaned 1N4004": "diode_iv_data.csv",
}

@st.cache_data
def read_dataset_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def voltage_current_columns(frame):
    """Return recognized voltage/current column names, or (None, None)."""
    pairs = [
        ("v_meas", "i_meas"), ("voltage_V", "current_A"),
        ("V_V", "I_A"), ("V", "I"), ("voltage", "current"),
    ]
    for v_col, i_col in pairs:
        if v_col in frame.columns and i_col in frame.columns:
            return v_col, i_col
    return None, None

def material_label(dataset_name, frame):
    if "material" in frame.columns:
        vals = frame["material"].dropna().astype(str).unique()
        if len(vals) == 1:
            return vals[0]
        if len(vals) > 1:
            return "Multiple materials"
    return dataset_name


def get_1n4004_measured_voltage_range(voltage):
    """Use the matching 1N4004 forward- or reverse-bias measurements."""
    dataset_key = "1N4004 reverse bias" if voltage < 0 else "1N4004 forward bias"
    frame = read_dataset_csv(DATASET_FILES[dataset_key])
    v_col, _ = voltage_current_columns(frame)
    if v_col is not None and not frame.empty:
        values = pd.to_numeric(frame[v_col], errors="coerce").dropna()
        if not values.empty:
            return float(values.min()), float(values.max()), dataset_key
    return None, None, dataset_key


models, model_errors = load_models()
data = load_data()
training_data = load_training_data()



PAGES = ["Home", "Project Guide", "Predictor", "Model Comparison", "Dataset Explorer"]

if "page" not in st.session_state:
    st.session_state.page = "Home"

def go_to(page):
    st.session_state.page = page

st.markdown("""
<style>
/* Give the top navigation its own clear stacking layer */
div[data-testid="stHorizontalBlock"]:has(button[key^="topnav_"]) {
    position: relative;
    z-index: 20;
}
</style>
""", unsafe_allow_html=True)

nav_cols = st.columns([1.25, 1.1, 1.0, 1.2, 1.2, 1.0], gap="small")

with nav_cols[0]:
    logo_col, name_col = st.columns([0.42, 1.55], gap="small", vertical_alignment="center")
    with logo_col:
        st.image("diodelab_favicon.png", width=38)
    with name_col:
        st.markdown(
            "<div style='display:flex;align-items:center;height:38px;"
            "padding:0;color:#f4f9ff;font-weight:850;font-size:1.38rem;"
            "line-height:1;letter-spacing:-.045em;white-space:nowrap;"
            "transform:translateY(-8px)'>"
            "<span>Diode</span><span style='color:#55d8f5'>Lab</span></div>",
            unsafe_allow_html=True,
        )

NAV_ITEMS = [
    ("Home", "Home", ":material/home:"),
    ("Project Guide", "Research", ":material/menu_book:"),
    ("Predictor", "Predictor", ":material/query_stats:"),
    ("Model Comparison", "Model lab", ":material/compare_arrows:"),
    ("Dataset Explorer", "Data", ":material/database:"),
]

for col, (target, label, icon_name) in zip(nav_cols[1:], NAV_ITEMS):
    with col:
        st.button(
            label,
            key=f"topnav_{target}",
            icon=icon_name,
            use_container_width=True,
            on_click=go_to,
            args=(target,),
        )

page = st.session_state.page




if model_errors:
    st.subheader("Model loading errors")
    for error in model_errors:
        st.error(error)
else:
    st.success("All saved models loaded successfully.")
valid_data = not data.empty and {"v_meas", "i_meas"}.issubset(data.columns)
if valid_data:
    vmin = float(data["v_meas"].min())
    vmax = float(data["v_meas"].max())
    imin = float(data["i_meas"].min())
    imax = float(data["i_meas"].max())
else:
    vmin, vmax, imin, imax = 0.0, 0.815, 0.0, 0.05

# ---------- Shared plotting helper ----------
def draw_iv_curve(show_models=False, selected_model=None, highlight_voltage=None):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    fig.patch.set_facecolor("#081326")
    ax.set_facecolor("#081326")
    if valid_data:
        ax.scatter(data["v_meas"], data["i_meas"], s=19, alpha=.78, label="Measured data")
    if show_models and models and valid_data:
        xs = np.linspace(vmin, vmax, 350).reshape(-1, 1)
        for label, model in models.items():
            if selected_model and label != selected_model:
                continue
            try:
                ys = np.asarray(model.predict(xs)).reshape(-1)
                ax.plot(xs.reshape(-1), ys, linewidth=2.2, label=f"{label} prediction")
            except Exception:
                pass
    if highlight_voltage is not None:
        ax.axvline(highlight_voltage, linestyle="--", linewidth=1.3, alpha=.8, label=f"Input: {highlight_voltage:.3f} V")
    ax.set_title("1N4004 forward-bias I–V characteristics", color="#eaf4ff", pad=12, fontsize=13)
    ax.set_xlabel("Measured voltage (V)", color="#a9c4df")
    ax.set_ylabel("Measured current (A)", color="#a9c4df")
    ax.tick_params(colors="#a9c4df")
    for spine in ax.spines.values():
        spine.set_color("#294563")
    ax.grid(True, alpha=.25, color="#52708e")
    ax.legend(facecolor="#10223b", edgecolor="#294563", labelcolor="#eaf4ff")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ---------- HOME ----------

if st.session_state.page == "Home":
    st.markdown("""
    <section class="hero">
      <div class="hero-topline"><span class="eyebrow">SEMICONDUCTOR DATA · MACHINE LEARNING</span><span class="hero-status"><span class="status-dot"></span> Interactive research workspace</span></div>
      <h1>Explore diode behaviour.<br><span class="gradient-text">Understand every curve.</span></h1>
      <p>Explore 1N4004 regression experiments alongside measured current–voltage characteristics of silicon and silicon-carbide power devices, with saved models and device-level data exploration in one workspace.</p>
      <div class="hero-actions"><span class="hero-chip">I–V analysis</span><span class="hero-chip">Model evaluation</span><span class="hero-chip">Silicon &amp; SiC data</span></div>
    </section>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-heading"><div><div class="section-kicker">Project at a glance</div><h2>Measurements into insight</h2><p class="small-muted">Separate views of the 1N4004 regression dataset and the classified silicon and SiC device measurements.</p></div></div>', unsafe_allow_html=True)

    # Avoid displaying a tiny floating-point negative value as "-0.000 V".
    vmin_display = 0.0 if abs(float(vmin)) < 0.0005 else float(vmin)
    vmax_display = 0.0 if abs(float(vmax)) < 0.0005 else float(vmax)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">1N4004 I–V observations</div><div class="metric-value">{len(data) if valid_data else "—"}</div><div class="metric-note">Measured voltage/current pairs</div></div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Voltage span</div><div class="metric-value">{vmin_display:.3f} V</div><div class="metric-note">to {vmax_display:.3f} V in the 1N4004 data</div></div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Saved estimators loaded</div><div class="metric-value">{len(models)}</div><div class="metric-note">Available model files</div></div>',
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Silicon &amp; SiC observations</div><div class="metric-value">{len(training_data):,}</div><div class="metric-note">Silicon and SiC device records</div></div>',
            unsafe_allow_html=True
        )

    st.write("")
    st.markdown('<div class="section-heading"><div><div class="section-kicker">Explore DiodeLab</div><h2>Choose where to begin</h2><p class="small-muted">Each workspace has a specific role in the analysis.</p></div></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3, gap="medium")
    with a:
        st.markdown('<div class="feature-card"><div class="feature-icon"><span>01</span></div><h3>Predictor</h3><p>Enter a voltage and explore current estimates from the available saved models.</p><div class="feature-tag">Interactive inference</div></div>', unsafe_allow_html=True)
        st.button("Open predictor", key="home_predictor", icon=":material/arrow_forward:", use_container_width=True, on_click=go_to, args=("Predictor",))
    with b:
        st.markdown('<div class="feature-card"><div class="feature-icon"><span>02</span></div><h3>Model lab</h3><p>Inspect recorded evaluation results and compare measured and predicted curves.</p><div class="feature-tag">Evaluation & comparison</div></div>', unsafe_allow_html=True)
        st.button("Explore model comparison", key="home_compare", icon=":material/arrow_forward:", use_container_width=True, on_click=go_to, args=("Model Comparison",))
    with c:
        st.markdown('<div class="feature-card"><div class="feature-icon"><span>03</span></div><h3>Data explorer</h3><p>Browse measurement tables, inspect variables, and download available datasets.</p><div class="feature-tag">Experimental evidence</div></div>', unsafe_allow_html=True)
        st.button("Browse datasets", key="home_data", icon=":material/arrow_forward:", use_container_width=True, on_click=go_to, args=("Dataset Explorer",))

    st.write("")
    st.markdown("""
    <div class="workflow-panel">
      <div class="section-kicker">How to use the workspace</div>
      <h2>From measurement to interpretation</h2>
      <div class="workflow-grid">
        <div><span class="workflow-number">1</span><strong>Start with the data</strong><p>Review the measured voltage, current, device, and temperature information.</p></div>
        <div><span class="workflow-number">2</span><strong>Explore a model</strong><p>Use the predictor with the saved estimators and supported input ranges.</p></div>
        <div><span class="workflow-number">3</span><strong>Compare evidence</strong><p>Interpret the displayed curves and recorded evaluation results carefully.</p></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Research note: model outputs are estimates within the scope of the available measurements and trained models. They should not be treated as component datasheet specifications or safety-critical design values.")

# ---------- PROJECT GUIDE ----------
elif st.session_state.page == "Project Guide":
    st.markdown('<div class="section-kicker">Research question and evidence</div>', unsafe_allow_html=True)
    st.title("Project guide")
    st.markdown("### Research question")
    st.write(
        "How well can regression models represent the measured current–voltage "
        "(I–V) relationship of a 1N4004 diode, and how do measured I–V curves "
        "for selected silicon and silicon-carbide power devices vary with "
        "voltage and temperature?"
    )
    st.markdown("### What does one row represent?")
    st.write(
        "In the 1N4004 table, one row is one measured voltage/current pair "
        "from a diode sweep. In the classified device table, one row is one "
        "measured voltage/current point for a named device at a stated "
        "temperature. Rows are measurement points, not separate physical devices."
    )

    st.markdown("### Data sources and scale")
    c1, c2, c3 = st.columns(3)
    c1.metric("1N4004 observations", f"{len(data):,}" if valid_data else "Unavailable")
    c2.metric("Classified device observations", f"{len(training_data):,}" if not training_data.empty else "Unavailable")
    c3.metric("Classified devices", f"{training_data['device'].nunique():,}" if not training_data.empty else "Unavailable")
    st.write(
        "The 1N4004 measurements are distributed with the project in "
        "`diode_iv_data.csv`. The external measurement collection is attributed "
        "to the Diode I–V Measurements repository and is licensed CC BY 4.0. "
        "The classified silicon and silicon-carbide device measurements are "
        "attributed in the data documentation to the Cryogenic and "
        "Superconducting Power Electronics Database (DOI: 10.57745/2AHLA6)."
    )
    st.markdown(
        "Sources: [Diode I–V Measurements](https://github.com/blueberrye-io/diode-iv-measurements/) · "
        "[Cryogenic and Superconducting Power Electronics Database](https://doi.org/10.57745/2AHLA6)"
    )
    if not training_data.empty:
        st.caption(
            f"The classified file used by the app contains {len(training_data):,} "
            f"complete rows across {training_data['device'].nunique()} devices "
            "in silicon and silicon carbide. The available measured temperatures "
            "in this file are 77 K and 293 K. Individual devices may have only "
            "these two measured temperature conditions; the app does not invent "
            "intermediate measurements."
        )

    st.markdown("### Variables and preprocessing")
    st.write(
        "The principal variables are measured voltage (V), measured current (A), "
        "device identifier, material, and temperature (K). The 1N4004 loader "
        "retains the voltage and current columns, removes rows with missing "
        "values, and sorts measurements by voltage. The classified-data loader "
        "checks for the required columns and removes rows missing device, "
        "voltage, current, or temperature. For material-model prediction, the "
        "application selects positive-current observations at the selected "
        "device and exact measured temperature."
    )
    st.write(
        "The source documentation flags readings below approximately 50 nA "
        "for cautious interpretation. The external review table also preserves "
        "near-zero negative readings with review notes rather than silently "
        "changing them. The classified table has 26 non-positive current rows; "
        "the predictor excludes these when constructing its material-model "
        "prediction subset."
    )

    st.markdown("### Models and baseline")
    st.write(
        "The displayed 1N4004 comparison includes Random Forest and tuned SVR, "
        "with Linear Regression and a mean-prediction baseline as reference "
        "models. The application also loads device/material SVR estimators for "
        "silicon and silicon-carbide measurements. These saved estimators are "
        "used for interactive inference; this page does not claim that the "
        "multi-device estimators were retrained during an app session."
    )

    st.markdown("### Evaluation and recorded results")
    st.write(
        "The following metrics are stored in the application as previously "
        "recorded results for a random holdout from the 1N4004 measurement "
        "sweep. MAE and RMSE are in amperes; lower is better. R² closer to 1 "
        "indicates a closer fit on the reported test set."
    )
    overview_metrics = pd.DataFrame([
        {"Model": "Random Forest", "MAE (A)": 0.0001714702, "RMSE (A)": 0.0004224828, "R²": 0.9989055},
        {"Model": "Tuned SVR", "MAE (A)": 0.0002631377, "RMSE (A)": 0.0003458506, "R²": 0.9992665},
        {"Model": "Linear Regression", "MAE (A)": 0.006944, "RMSE (A)": 0.009559, "R²": 0.439677},
        {"Model": "Mean baseline", "MAE (A)": 0.008777, "RMSE (A)": 0.012815, "R²": -0.007052},
    ])
    st.dataframe(overview_metrics, use_container_width=True, hide_index=True)
    st.write(
        "On the reported metrics, tuned SVR has the lowest RMSE and highest R², "
        "while Random Forest has the lowest MAE. This means the ranking depends "
        "on the error measure: SVR has the smaller squared-error penalty overall, "
        "but Random Forest has the smaller average absolute error. Both reported "
        "machine-learning models outperform the displayed baselines on these "
        "stored values."
    )
    st.warning(
        "Reproducibility gap: the submitted repository does not include the "
        "original training notebooks/scripts, exact random split indices, "
        "split sizes, or per-observation residuals for these metrics. The "
        "metrics are therefore reported as stored results, not independently "
        "recomputed here. The exact split configuration and detailed error "
        "analysis must be added from the original experiment records before "
        "claiming full reproduction."
    )

    st.markdown("### Interactive data exploration")
    if not training_data.empty:
        guide_devices = sorted(training_data["device"].astype(str).unique().tolist())
        guide_device = st.selectbox("Explore a measured device", guide_devices, key="guide_device")
        guide_frame = training_data[training_data["device"].astype(str).eq(guide_device)].copy()
        guide_temps = sorted(pd.to_numeric(guide_frame["temperature_K"], errors="coerce").dropna().unique().tolist())
        if guide_temps:
            guide_temp = st.selectbox("Measured temperature (K)", guide_temps, key="guide_temperature")
            guide_frame = guide_frame[pd.to_numeric(guide_frame["temperature_K"], errors="coerce").eq(float(guide_temp))]
            guide_frame["voltage_V"] = pd.to_numeric(guide_frame["voltage_V"], errors="coerce")
            guide_frame["current_A"] = pd.to_numeric(guide_frame["current_A"], errors="coerce")
            guide_frame = guide_frame.dropna(subset=["voltage_V", "current_A"]).sort_values("voltage_V")
            st.caption(f"{len(guide_frame)} measured points for {guide_device} at {guide_temp:g} K.")
            if not guide_frame.empty:
                st.line_chart(guide_frame.set_index("voltage_V")["current_A"], x_label="Voltage (V)", y_label="Current (A)")

    st.markdown("### Limitations")
    st.markdown(
        "- The reported 1N4004 scores come from a random holdout within one measured sweep; nearby points may be correlated.\n"
        "- The available classified silicon and silicon-carbide measurements cover 77 K and 293 K only. Predictions at unmeasured temperatures are not supported by the dataset interface.\n"
        "- Device-specific measurements are sparse compared with large-scale datasets, and device coverage is uneven.\n"
        "- Model performance outside the measured voltage, temperature, and device conditions is not established.\n"
        "- The repository currently lacks the exact training workflow and split artifacts needed to independently reproduce all reported scores."
    )
    st.markdown("### Reproducibility and repository")
    st.write(
        "See the README and `docs/REPRODUCIBILITY.md` for setup, data provenance, "
        "the preprocessing summary, known gaps, and instructions for running "
        "the application and basic physics checks."
    )

# ---------- PREDICTOR ----------

elif st.session_state.page == "Predictor":
    st.markdown(
        '<div class="section-kicker">Interactive inference</div>',
        unsafe_allow_html=True,
    )
    st.title("Diode current predictor")
    st.write(
        "Choose a trained model and enter a voltage. "
        "Predictions outside the measured voltage range may be unreliable."
    )

    if not models:
        st.error(
            "No saved models loaded. Confirm the model .joblib files "
            "are in the repository."
        )
    else:
        # Select the device/material FIRST. Only then show compatible models.
        device_type = st.selectbox(
            "1. Choose device / material",
            [
                "1N4004",
                "Silicon",
                "Silicon carbide (SiC)",
              
            ],
            key="predict_device_type",
        )

        device = device_type
        device_rows = pd.DataFrame()

        if device_type == "1N4004":
            compatible_models = [
                name for name in (
                    "Random Forest",
                    "Tuned SVR",
                    "1N4004 Reverse-bias SVR",
                )
                if name in models
            ]
            device = "1N4004"
        else:
            material_name = {
                "Silicon": "silicon",
                "Silicon carbide (SiC)": "silicon carbide",
                
            }[device_type]
            device_rows_for_material = training_data[
                training_data["material"].astype(str).str.strip().str.lower().eq(material_name)
            ] if not training_data.empty else pd.DataFrame()

            available_devices = (
                device_rows_for_material["device"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ) if not device_rows_for_material.empty else []

            if device_type == "Silicon":
                trained_silicon_devices = [
                    "1N11877R",
                    "1N1190",
                    "1N3913",
                    "45L120",
                    "BYX661000",
                    "BZW12360",
                    "BZW1336",
                    "BZW1347",
                    "MBR4035",
                ]

                device_options = sorted(
                    set(trained_silicon_devices).intersection(available_devices)
                )
            else:
                device_options = sorted(available_devices)
            if device_options:
                device = st.selectbox(
                    "2. Choose device",
                    device_options,
                    key=f"predict_device_{device_type}",
                )
                device_rows = device_rows_for_material[
                    device_rows_for_material["device"].astype(str).eq(device)
                ].copy()
            else:
                device = None
                st.warning(f"No {device_type} devices were found in the combined dataset.")

            model_by_material = {
                "Silicon": ["Silicon multi-temperature SVR", "Silicon SVR"],
                "Silicon carbide (SiC)": ["SiC multi-temperature SVR", "SiC SVR"],
                
            }
            compatible_models = [
                name for name in model_by_material[device_type] if name in models
            ]

        # Model selection is deliberately BELOW device/material selection.
        if compatible_models:
            model_name = st.selectbox(
                "2. Choose model" if device_type == "1N4004" else "3. Choose model",
                compatible_models,
                key=f"predict_model_{device_type}",
            )
        else:
            model_name = None
            st.error("No compatible trained model is available for this device/material.")

        # Temperature is relevant to material-specific models, not the original 1N4004 models.
        temperature = 293.0
        if device_type != "1N4004" and device is not None and not device_rows.empty:
            available_temperatures = sorted(
                pd.to_numeric(device_rows["temperature_K"], errors="coerce")
                .dropna().unique().astype(float).tolist()
            )
            if available_temperatures:
                temperature = st.selectbox(
                    "4. Choose measured temperature (K)",
                    available_temperatures,
                    index=min(range(len(available_temperatures)), key=lambda i: abs(available_temperatures[i] - 293.0)),
                    key=f"predict_temperature_{device_type}_{device}",
                )
            else:
                st.warning("No measured temperatures were found for this device.")

        # No min_value/max_value: voltage is intentionally unrestricted.
        voltage = st.number_input(
            "5. Enter voltage (V)",
            value=0.70,
            step=0.005,
            format="%.5f",
            key="predict_voltage",
        )

        # Warn when voltage is outside the selected device's recorded range.
        
        # Warn when voltage is outside the selected device's recorded range.
        if device_type != "1N4004" and device is not None and not device_rows.empty:
            at_temperature = device_rows[
                pd.to_numeric(device_rows["temperature_K"], errors="coerce").eq(float(temperature))
            ]
            if not at_temperature.empty:
                measured_min = float(at_temperature["voltage_V"].min())
                measured_max = float(at_temperature["voltage_V"].max())
                st.caption(
                    f"Recorded voltage range for {device} at {temperature:g} K: "
                    f"{measured_min:.5g} to {measured_max:.5g} V."
                )
                if voltage < measured_min or voltage > measured_max:
                    st.warning("The voltage is outside this device's recorded range; the prediction may be unreliable.")

        elif device_type == "1N4004":
            range_min, range_max, range_dataset = get_1n4004_measured_voltage_range(voltage)
            if range_min is not None and (voltage < range_min or voltage > range_max):
                st.warning(
                    f"The voltage is outside the 1N4004 {range_dataset} measured range "
                    f"({range_min:.5g} to {range_max:.5g} V). "
                    "The prediction may be unreliable."
                )
            elif range_min is None:
                st.warning(f"Could not load the matching 1N4004 {range_dataset} voltage range.")

       
        # Explain the polarity supported by the selected device/model.
        if device_type == "1N4004":
            if model_name == "1N4004 Reverse-bias SVR":
                if voltage > 0:
                    st.warning(
                        "Forward bias: the selected 1N4004 model was trained "
                        "using reverse-bias measurements. Its forward-current "
                        "prediction is not validated. Select Random Forest or "
                        "Tuned SVR instead."
                    )
                elif voltage < 0:
                    st.info(
                        "Reverse bias: the selected model was trained using "
                        "1N4004 reverse-bias measurements. Its predictions "
                        "are still estimates."
                    )
            elif voltage < 0:
                st.warning(
                    "Reverse bias: the selected 1N4004 model was trained "
                    "using forward-bias measurements. Its reverse-current "
                    "prediction is not validated. Select the "
                    "1N4004 Reverse-bias SVR instead."
                )

        elif device_type in ("Silicon", "Silicon carbide (SiC)"):
            if voltage < 0:
                st.warning(
                    "Reverse bias: the available measurements for this "
                    "material contain no negative-voltage data. The selected "
                    "model is not validated for reverse-bias predictions."
                )

       
            


        if st.button("Predict current", key="predict_button"):
            # Clear the previous result before attempting a new prediction.
            st.session_state.pop("last_prediction", None)

            try:
                if model_name in ["Silicon SVR", "SiC SVR", "Silicon multi-temperature SVR", "SiC multi-temperature SVR" ]:
                    if training_data.empty:
                        st.error("The training dataset could not be loaded.")
                    else:
                        device_data = training_data[
                            (training_data["device"] == device)
                            & (training_data["temperature_K"] == temperature)
                            & (training_data["current_A"] > 0)
                        ]

                        if device_data.empty:
                            st.error(
                                f"No measured data is available for {device} "
                                f"at exactly {temperature:g} K. "
                                "Choose a temperature with measured data."
                            )
                        else:
                            min_voltage = float(
                                device_data["voltage_V"].min()
                            )
                            max_voltage = float(
                                device_data["voltage_V"].max()
                            )

                            model_input = pd.DataFrame([{
                                "device": device,
                                "voltage_V": voltage,
                                "temperature_K": temperature,
                            }])

                            model_output = float(
                                models[model_name].predict(model_input)[0]
                            )
                            if model_name in ["Silicon multi-temperature SVR", "SiC multi-temperature SVR"]:
                                # New multi-temperature wrappers return current in amperes directly.
                                current = model_output
                            else:
                                # Legacy material-specific models return log10(current).
                                current = 10 ** model_output

                            st.session_state.last_prediction = {
                                "model": model_name,
                                "device": device,
                                "voltage": voltage,
                                "temperature": temperature,
                                "current": current,
                            }

                elif model_name == "1N4004 Reverse-bias SVR":
                    # This model predicts log10(current), so convert back to amperes.
                    model_input = pd.DataFrame({"v_meas": [voltage]})

                    predicted_log_current = float(
                        models[model_name].predict(model_input)[0]
                    )
                    current = 10 ** predicted_log_current

                    if not np.isfinite(current) or current <= 0:
                        st.error("The reverse-bias model returned an invalid prediction.")
                    else:
                        st.session_state.last_prediction = {
                            "model": model_name,
                            "device": device,
                            "voltage": voltage,
                            "temperature": temperature,
                            "current": current,
                        }

                else:
                    # Original models use voltage as their only input.
                    current = float(
                        np.asarray(
                            models[model_name].predict(
                                np.array([[voltage]])
                            )
                        ).reshape(-1)[0]
                    )

                    if not np.isfinite(current):
                        st.error("The model returned a non-finite prediction.")
                    else:
                        st.session_state.last_prediction = {
                            "model": model_name,
                            "device": device,
                            "voltage": voltage,
                            "temperature": temperature,
                            "current": current,
                        }

            except Exception as exc:
                st.session_state.pop("last_prediction", None)
                st.error(f"Prediction failed: {exc}")

        # Show a result only when it matches the current inputs.
        result = st.session_state.get("last_prediction")

        if result and (
            result["model"] != model_name
            or result["device"] != device
            or result["voltage"] != voltage
            or result["temperature"] != temperature
        ):
            result = None

        if result:
            st.markdown("### Prediction result")

            m1, m2, m3 = st.columns(3)
            m1.metric(
                "Predicted current",
                f'{result["current"]:.6g} A',
            )
            m2.metric(
                "Equivalent current",
                f'{result["current"] * 1000:.6g} mA',
            )
            m3.metric("Model", result["model"])

            if result["model"] in ["Silicon SVR", "SiC SVR", "Silicon multi-temperature SVR", "SiC multi-temperature SVR"]:
                st.info(
                    f"Estimate for {result['device']} at "
                    f"{result['temperature']:g} K. "
                    "The voltage is within the measured range for this "
                    "device and temperature, but the estimate is not "
                    "a guaranteed physical measurement."
                )
            elif result["device"] == "1N4004":
                result_min, result_max, result_dataset = get_1n4004_measured_voltage_range(result["voltage"])
                if result_min is not None and not (result_min <= result["voltage"] <= result_max):
                    st.warning(
                        f'{result["voltage"]:.5f} V is outside the 1N4004 {result_dataset} '
                        f"measured range ({result_min:.5f}–{result_max:.5f} V). "
                        "Treat this prediction as an extrapolation."
                    )
                elif result["voltage"] < 0:
                    if result["model"] == "1N4004 Reverse-bias SVR":
                        st.warning(
                            "This estimate uses the 1N4004 reverse-bias model. "
                            "It is based on measured reverse-bias data, but its "
                            "accuracy is limited and it should not be treated "
                            "as a guaranteed physical measurement."
                        )
                    else:
                        st.warning(
                            "The selected model was trained on forward-bias data only. "
                            "Its reverse-current prediction is not validated."
                        )
                    st.info("This is a model estimate, not a guaranteed physical measurement.")
            else:
                st.info(
                    "This is a model estimate, not a guaranteed "
                    "physical measurement."
                )

            with st.expander("How should I interpret this prediction?"):
                st.write(f"Model: {result['model']}")
                st.write(f"Device: {result['device']}")
                st.write(f"Voltage: {result['voltage']:.5f} V")
                st.write(f"Temperature: {result['temperature']:g} K")
                st.write(
                    f"Estimated current: {result['current']:.6g} A "
                    f"({result['current'] * 1000:.6g} mA)"
                )
                st.write(
                    "A prediction inside the measured voltage range can "
                    "still be inaccurate. These models are estimates, "
                    "not substitutes for physical measurements."
                )





        st.markdown("### Interactive I–V graph")
        st.caption(
            "Use the graph toolbar to zoom, pan, or reset. Hover over a curve to see "
            "the exact voltage and current. The gold star marks the latest successful "
            "prediction for the current inputs. Choose Forward or Reverse view to avoid "
            "the negative-voltage range compressing the positive-voltage region."
        )

        # Keep the existing dataset choices; this update does not add or retrain datasets.
        
           
        
        
        # Allow comparison across all trained materials and devices.
        selected_curves = []
        comparison_options = []

        # Add the 1N4004 measured forward- and reverse-bias curves.
        comparison_options.extend([
            ("1N4004 forward bias", "dataset", "1N4004 forward bias"),
            ("1N4004 reverse bias", "dataset", "1N4004 reverse bias"),
        ])

        # Add every device available in the classified training data.
        if not training_data.empty:
            available_devices = (
                training_data[["material", "device"]]
                .dropna()
                .drop_duplicates()
            )

            for _, row in available_devices.iterrows():
                comparison_device = str(row["device"])
                comparison_material = str(row["material"])

                if (
                    device_type != "1N4004"
                    and comparison_device == str(device)
                ):
                    continue

                label = f"{comparison_device} ({comparison_material})"

                comparison_options.append(
                    (
                        label,
                        "device",
                        comparison_device,
                    )
                )

        st.caption(
            "Select any available device or measured curve to compare. "
            "Devices from different materials can be compared together."
        )

        check_cols = st.columns(3)

        for idx, (label, option_type, option_value) in enumerate(
            comparison_options
        ):
            with check_cols[idx % 3]:
                default_checked = (
                    option_type == "dataset"
                    and (
                        (voltage >= 0 and option_value == "1N4004 forward bias")
                        or (voltage < 0 and option_value == "1N4004 reverse bias")
                    )
                )

                if st.checkbox(
                    label,
                    value=default_checked,
                    key=f"curve_check_{option_type}_{label}",
                ):
                    selected_curves.append(
                        (label, option_type, option_value)
                    )

        # Automatically display the selected material-specific device.
        curve_data = []

        if (
            device_type != "1N4004"
            and device is not None
            and not device_rows.empty
        ):
            selected_device_data = device_rows.copy()

            selected_device_data["temperature_K"] = pd.to_numeric(
                selected_device_data["temperature_K"],
                errors="coerce",
            )

            selected_device_data = selected_device_data[
                selected_device_data["temperature_K"] == float(temperature)
            ]

            curve = selected_device_data[
                ["voltage_V", "current_A"]
            ].copy()

            curve.columns = ["voltage", "current"]

            curve["voltage"] = pd.to_numeric(
                curve["voltage"], errors="coerce"
            )
            curve["current"] = pd.to_numeric(
                curve["current"], errors="coerce"
            )

            curve = (
                curve.replace([np.inf, -np.inf], np.nan)
                .dropna()
                .sort_values("voltage")
            )

            if not curve.empty:
                curve_data.append(
                    (
                        f"Selected device: {device} ({temperature:g} K)",
                        curve,
                    )
                )

        # Add all selected comparison curves.
        for label, option_type, option_value in selected_curves:

            if option_type == "dataset":
                frame = read_dataset_csv(DATASET_FILES[option_value])
                v_col, i_col = voltage_current_columns(frame)

                if v_col is None:
                    continue

                curve = frame[[v_col, i_col]].copy()
                curve.columns = ["voltage", "current"]

            else:
                comparison_data = training_data[
                    training_data["device"].astype(str) == option_value
                ].copy()

                comparison_data["temperature_K"] = pd.to_numeric(
                    comparison_data["temperature_K"],
                    errors="coerce",
                )

                available_temps = (
                    comparison_data["temperature_K"]
                    .dropna()
                    .unique()
                )

                if len(available_temps) == 0:
                    continue

                nearest_temp = min(
                    available_temps,
                    key=lambda t: abs(float(t) - float(temperature)),
                )

                comparison_data = comparison_data[
                    comparison_data["temperature_K"] == nearest_temp
                ]

                curve = comparison_data[
                    ["voltage_V", "current_A"]
                ].copy()

                curve.columns = ["voltage", "current"]

                label = f"{label} ({nearest_temp:g} K)"

            curve["voltage"] = pd.to_numeric(
                curve["voltage"], errors="coerce"
            )
            curve["current"] = pd.to_numeric(
                curve["current"], errors="coerce"
            )

            curve = (
                curve.replace([np.inf, -np.inf], np.nan)
                .dropna()
                .sort_values("voltage")
            )

            if not curve.empty:
                curve_data.append((label, curve))




        result_for_graph = st.session_state.get("last_prediction")
        result_matches_inputs = bool(
            result_for_graph
            and result_for_graph.get("model") == model_name
            and result_for_graph.get("device") == device
            and result_for_graph.get("voltage") == voltage
            and result_for_graph.get("temperature") == temperature
        )
        if result_matches_inputs:
            try:
                result_matches_inputs = np.isfinite(float(result_for_graph["current"]))
            except (TypeError, ValueError, KeyError):
                result_matches_inputs = False

        all_voltages = []
        for _, curve in curve_data:
            all_voltages.extend(curve["voltage"].astype(float).tolist())
        if result_matches_inputs:
            all_voltages.append(float(result_for_graph["voltage"]))

        if all_voltages:
            data_vmin, data_vmax = float(min(all_voltages)), float(max(all_voltages))
            if data_vmin == data_vmax:
                data_vmin -= 0.1
                data_vmax += 0.1
        else:
            data_vmin, data_vmax = -1.0, 1.0

        view_mode = st.selectbox(
            "Voltage view",
            [
                "Full voltage range",
                "Forward bias (0 V and above)",
                "Reverse bias (below 0 V)",
                "Zoom around selected voltage",
                "Custom voltage range",
            ],
            key="iv_graph_view",
        )

        if view_mode == "Full voltage range":
            x_range = [data_vmin, data_vmax]
        elif view_mode == "Forward bias (0 V and above)":
            positive = [v for v in all_voltages if v >= 0]
            x_range = [0.0, max(positive)] if positive else [0.0, 1.0]
            if x_range[0] == x_range[1]:
                x_range[1] = x_range[0] + 0.1
        elif view_mode == "Reverse bias (below 0 V)":
            negative = [v for v in all_voltages if v < 0]
            x_range = [min(negative), 0.0] if negative else [-1.0, 0.0]
        elif view_mode == "Zoom around selected voltage":
            width = st.slider(
                "Voltage window width (V)",
                min_value=0.01,
                max_value=10.0,
                value=0.5,
                step=0.01,
                key="iv_zoom_width",
            )
            x_range = [float(voltage) - width / 2, float(voltage) + width / 2]
        else:
            # Number inputs allow a custom range even when data spans a wide voltage interval.
            left_col, right_col = st.columns(2)
            with left_col:
                x_min = st.number_input(
                    "Minimum visible voltage (V)",
                    value=float(data_vmin),
                    key="iv_custom_x_min",
                )
            with right_col:
                x_max = st.number_input(
                    "Maximum visible voltage (V)",
                    value=float(data_vmax),
                    key="iv_custom_x_max",
                )
            if x_min >= x_max:
                st.warning("The maximum voltage must be greater than the minimum voltage.")
                x_range = [data_vmin, data_vmax]
            else:
                x_range = [float(x_min), float(x_max)]

        # Plotly does not offer a native symmetric-log axis. Transform y positions for
        # display, while hover tooltips continue to show the original current in amperes.
        linthresh = 1e-9

        def symlog_transform(values):
            values = np.asarray(values, dtype=float)
            return np.sign(values) * np.log10(1.0 + np.abs(values) / linthresh)

        fig = go.Figure()
        for curve_label, curve in curve_data:
            currents = curve["current"].to_numpy(dtype=float)
            fig.add_trace(
                go.Scatter(
                    x=curve["voltage"],
                    y=symlog_transform(currents),
                    customdata=currents,
                    mode="lines+markers",
                    name=curve_label,
                    line={"width": 2},
                    marker={"size": 4},
                    hovertemplate=(
                        "Voltage: %{x:.6g} V<br>Current: %{customdata:.6g} A"
                        "<extra>%{fullData.name}</extra>"
                    ),
                )
            )

        if result_matches_inputs:
            pred_v = float(result_for_graph["voltage"])
            pred_i = float(result_for_graph["current"])
            fig.add_trace(
                go.Scatter(
                    x=[pred_v],
                    y=symlog_transform([pred_i]),
                    customdata=[pred_i],
                    mode="markers",
                    name="Predicted current",
                    marker={
                        "symbol": "star",
                        "size": 18,
                        "color": "#ffcc66",
                        "line": {"color": "white", "width": 1.5},
                    },
                    hovertemplate=(
                        "<b>MODEL PREDICTION</b><br>Voltage: %{x:.6g} V<br>"
                        "Predicted current: %{customdata:.6g} A<extra></extra>"
                    ),
                )
            )

        fig.add_vline(
            x=float(voltage),
            line_dash="dash",
            line_width=1.3,
            line_color="#9dbcf4",
            annotation_text=f"Selected: {voltage:.4g} V",
            annotation_position="top",
        )

        tick_currents = np.array([
            -1.0, -0.1, -0.01, -0.001, -1e-4, -1e-5, -1e-6,
            -1e-7, -1e-8, -1e-9, 0.0, 1e-9, 1e-8, 1e-7,
            1e-6, 1e-5, 1e-4, 0.001, 0.01, 0.1, 1.0,
        ])
        fig.update_layout(
            title="Diode I–V characteristics",
            template="plotly_dark",
            height=650,
            autosize=True,
            margin={"l": 85, "r": 30, "t": 75, "b": 100},
            paper_bgcolor="#081326",
            plot_bgcolor="#081326",
            hovermode="closest",
            legend={
                "bgcolor": "rgba(16,34,59,0.9)",
                "bordercolor": "#294563",
                "borderwidth": 1,
            },
            xaxis={
                "title": "Voltage (V) — negative: reverse bias; positive: forward bias",
                "range": x_range,
                "showgrid": True,
                "gridcolor": "rgba(82,112,142,0.3)",
                "zeroline": True,
                "zerolinecolor": "#7890ad",
                "automargin": True,
            },
            yaxis={
                "title": "Current (A, symmetric-log scale)",
                "tickmode": "array",
                "tickvals": symlog_transform(tick_currents),
                "ticktext": [f"{value:.0e}" if value else "0" for value in tick_currents],
                "showgrid": True,
                "gridcolor": "rgba(82,112,142,0.3)",
                "zeroline": True,
                "zerolinecolor": "#7890ad",
                "automargin": True,
            },
        )

        if not curve_data and not result_matches_inputs:
            st.info(
                "Select one or more datasets above to display curves. "
                "The prediction marker appears after a successful prediction."
            )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"scrollZoom": True, "displaylogo": False, "responsive": True},
            key="interactive_iv_plot",
        )

# ---------- MODEL COMPARISON ----------
elif st.session_state.page == "Model Comparison":
    st.markdown('<div class="section-kicker">Evaluation</div>', unsafe_allow_html=True)
    st.title("Model comparison")
    st.write(
        "Explore the saved models by diode family. The 1N4004 section shows "
        "the previously recorded held-out metrics. Silicon and SiC sections "
        "show measured-versus-predicted I–V curves using the saved estimators; "
        "no evaluation scores are displayed for those families because a "
        "verified metrics file is not included in this repository."
    )

    family = st.selectbox(
        "Choose diode family",
        ["1N4004", "Silicon", "Silicon carbide (SiC)"],
        key="comparison_family",
    )

    if family == "1N4004":
        st.subheader("1N4004 — recorded model evaluation")
        metrics = pd.DataFrame([
            {"Model": "Random Forest", "MAE (A)": 0.0001714702, "RMSE (A)": 0.0004224828, "R²": 0.9989055},
            {"Model": "Tuned SVR", "MAE (A)": 0.0002631377, "RMSE (A)": 0.0003458506, "R²": 0.9992665},
            {"Model": "Linear Regression", "MAE (A)": 0.006944, "RMSE (A)": 0.009559, "R²": 0.439677},
            {"Model": "Mean baseline", "MAE (A)": 0.008777, "RMSE (A)": 0.012815, "R²": -0.007052},
        ])
        st.dataframe(metrics, use_container_width=True, hide_index=True)
        left, right = st.columns(2)
        with left:
            st.markdown("#### Mean absolute error")
            st.bar_chart(metrics.set_index("Model")[["MAE (A)"]])
        with right:
            st.markdown("#### Root mean squared error")
            st.bar_chart(metrics.set_index("Model")[["RMSE (A)"]])
        st.info(
            "These scores come from a random holdout within one measured 1N4004 "
            "voltage sweep. Nearby measurements may be correlated; the results "
            "do not establish generalization to other devices, temperatures, "
            "or measurement setups."
        )
        available_models = [
            name for name in ("Random Forest", "Tuned SVR", "1N4004 Reverse-bias SVR")
            if name in models
        ]
        if available_models and valid_data:
            st.markdown("#### 1N4004 prediction curve")
            selected_1n = st.selectbox(
                "Choose a 1N4004 model", available_models, key="comparison_1n_model"
            )
            draw_iv_curve(show_models=True, selected_model=selected_1n)
        else:
            st.warning("The 1N4004 model or original measured dataset is unavailable.")

    else:
        material_value = "silicon" if family == "Silicon" else "silicon carbide"
        material_rows = training_data[
            training_data["material"].astype(str).str.lower().eq(material_value)
        ].copy() if not training_data.empty else pd.DataFrame()

        model_options = (
            ["Silicon SVR", "Silicon multi-temperature SVR"]
            if material_value == "silicon"
            else ["SiC SVR", "SiC multi-temperature SVR"]
        )
        available_models = [name for name in model_options if name in models]

        if material_rows.empty:
            st.warning(f"No classified {family} measurements were found in the training dataset.")
        elif not available_models:
            st.error(f"No saved {family} prediction models could be loaded. Check the model files and deployment logs.")
        else:
            st.subheader(f"{family} — measured and predicted I–V curve")
            st.caption(
                "Select a device and one of the temperatures present in the "
                "classified measurements. The model receives device, voltage, "
                "and temperature as inputs."
            )
            devices = sorted(material_rows["device"].dropna().astype(str).unique().tolist())
            selected_device = st.selectbox(
                "Measured device", devices, key=f"comparison_device_{material_value}"
            )
            device_rows = material_rows[
                material_rows["device"].astype(str).eq(selected_device)
            ].copy()
            temperatures = sorted(
                pd.to_numeric(device_rows["temperature_K"], errors="coerce").dropna().unique().tolist()
            )
            if not temperatures:
                st.warning("No measured temperatures are available for this device.")
            else:
                selected_temperature = st.selectbox(
                    "Measured temperature (K)", temperatures,
                    index=min(range(len(temperatures)), key=lambda i: abs(temperatures[i] - 293.0)),
                    key=f"comparison_temperature_{material_value}_{selected_device}",
                )
                selected_model = st.selectbox(
                    "Prediction model", available_models,
                    key=f"comparison_model_{material_value}",
                )
                measured = device_rows[
                    pd.to_numeric(device_rows["temperature_K"], errors="coerce").eq(float(selected_temperature))
                ].copy()
                measured["voltage_V"] = pd.to_numeric(measured["voltage_V"], errors="coerce")
                measured["current_A"] = pd.to_numeric(measured["current_A"], errors="coerce")
                measured = measured.dropna(subset=["voltage_V", "current_A"]).sort_values("voltage_V")
                measured = measured[measured["current_A"] > 0]

                if measured.empty:
                    st.warning("There are no positive-current measured points to plot at this temperature.")
                else:
                    voltage_values = np.linspace(
                        float(measured["voltage_V"].min()),
                        float(measured["voltage_V"].max()), 250
                    )
                    prediction_inputs = pd.DataFrame({
                        "device": [selected_device] * len(voltage_values),
                        "voltage_V": voltage_values,
                        "temperature_K": [float(selected_temperature)] * len(voltage_values),
                    })
                    try:
                        predicted_current = np.asarray(
                            models[selected_model].predict(prediction_inputs)
                        ).reshape(-1)
                        plot_frame = pd.DataFrame({
                            "Voltage (V)": voltage_values,
                            "Predicted current (A)": predicted_current,
                        })
                        measured_frame = measured[["voltage_V", "current_A"]].rename(
                            columns={"voltage_V": "Voltage (V)", "current_A": "Measured current (A)"}
                        )
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=measured_frame["Voltage (V)"],
                            y=measured_frame["Measured current (A)"],
                            mode="markers", name="Measured data",
                            marker={"size": 6},
                        ))
                        fig.add_trace(go.Scatter(
                            x=plot_frame["Voltage (V)"],
                            y=plot_frame["Predicted current (A)"],
                            mode="lines", name=f"{selected_model} prediction",
                            line={"width": 2.5},
                        ))
                        fig.update_layout(
                            title=f"{selected_device} · {selected_temperature:g} K · {family}",
                            xaxis_title="Voltage (V)",
                            yaxis_title="Current (A)",
                            template="plotly_dark",
                            height=520,
                            legend={"orientation": "h", "y": 1.12},
                        )
                        fig.update_yaxes(type="log", title="Current (A, log scale)")
                        st.plotly_chart(fig, use_container_width=True)
                        st.caption(
                            f"Measured points: {len(measured):,}. Prediction shown only "
                            f"over the measured voltage range ({measured['voltage_V'].min():.4g} to "
                            f"{measured['voltage_V'].max():.4g} V)."
                        )
                    except Exception as exc:
                        st.error(
                            "The selected saved model could not generate this comparison. "
                            "The model expects the device, voltage_V, and temperature_K "
                            f"features. Technical detail: {exc}"
                        )
            st.info(
                "No MAE, RMSE, or R² scores are shown here because the repository "
                "does not include a verified held-out evaluation table for these "
                "material models. The chart is a measured-versus-model prediction "
                "visualisation, not a new independent test-set evaluation."
            )

# ---------- DATASET EXPLORER ----------
elif st.session_state.page == "Dataset Explorer":
    st.markdown('<div class="section-kicker">Experimental measurements</div>', unsafe_allow_html=True)
    st.title("Dataset explorer")
    available = {
        name: path for name, path in DATASET_FILES.items()
        if os.path.exists(path)
    }
    if not available:
        st.error("No CSV datasets were found in the expected repository folders.")
    else:
        chosen = st.selectbox("Choose a dataset", list(available.keys()))
        frame = read_dataset_csv(available[chosen])

        # Hide any GaN rows if a combined/source CSV is replaced later.
        if not frame.empty:
            gan_columns = [
                column for column in ["material", "device", "technology"]
                if column in frame.columns
            ]
            if gan_columns:
                is_gan = (
                    frame[gan_columns]
                    .astype(str)
                    .apply(
                        lambda column: column.str.contains(
                            r"\bgan\b|gallium nitride",
                            case=False,
                            regex=True,
                            na=False,
                        )
                    )
                    .any(axis=1)
                )
                frame = frame[~is_gan].copy()

        if frame.empty:
            st.error("This CSV could not be read or contains no rows.")
        else:
            st.write(f"**{chosen}** — {len(frame):,} rows and {len(frame.columns)} columns.")
            st.dataframe(frame.head(500), use_container_width=True, hide_index=True)
            st.download_button(
                "Download this dataset",
                frame.to_csv(index=False).encode("utf-8"),
                file_name=os.path.basename(available[chosen]),
                mime="text/csv",
            )
            v_col, i_col = voltage_current_columns(frame)
            if v_col is not None:
                plot_frame = frame[[v_col, i_col]].copy()
                plot_frame[v_col] = pd.to_numeric(plot_frame[v_col], errors="coerce")
                plot_frame[i_col] = pd.to_numeric(plot_frame[i_col], errors="coerce")
                plot_frame = plot_frame.dropna().sort_values(v_col)
                st.markdown("### I–V curve")
                fig, ax = plt.subplots(figsize=(10, 4.8))
                fig.patch.set_facecolor("#081326")
                ax.set_facecolor("#081326")
                ax.plot(plot_frame[v_col], plot_frame[i_col], marker=".", markersize=3, linewidth=1.5, label=chosen)
                ax.set_xlabel("Voltage (V)", color="#a9c4df")
                ax.set_ylabel("Current (A)", color="#a9c4df")
                ax.set_title(f"{chosen}: measured I–V curve", color="#eaf4ff")
                ax.tick_params(colors="#a9c4df")
                for spine in ax.spines.values():
                    spine.set_color("#294563")
                ax.grid(True, alpha=.25, color="#52708e")
                ax.legend(facecolor="#10223b", edgecolor="#294563", labelcolor="#eaf4ff")
                fig.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            else:
                st.info("This dataset does not contain a recognized voltage/current column pair.")

st.markdown("---")
st.markdown('<p class="small-muted">DiodeLab · Educational ML demonstration · Predictions are estimates based on one measured 1N4004 voltage sweep.</p>', unsafe_allow_html=True)





