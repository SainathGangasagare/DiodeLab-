/* Browser rendering of the original app.py pages. Original wording, navigation,
   estimator behavior, filters, and chart calculations are retained. */
(() => {
  'use strict';

  const PAGES = [
    ['Home', 'page-home'],
    ['Project Guide', 'page-guide'],
    ['Predictor', 'page-predictor'],
    ['Model Comparison', 'page-comparison'],
    ['Dataset Explorer', 'page-datasets'],
  ];
  const DATASET_FILES = {
    '1N4004 forward bias': 'python-app/data/external/1n4004_forward.csv',
    '1N4004 reverse bias': 'python-app/data/external/1n4004_reverse.csv',
    '1N4004 reverse bias (10 µA range)': 'python-app/data/external/1n4004_reverse_10uA_range.csv',
    '1N5229B Zener reverse bias': 'python-app/data/external/1n5229b_reverse.csv',
    'SB560 forward bias': 'python-app/data/external/sb560_forward.csv',
    'SB560 reverse bias': 'python-app/data/external/sb560_reverse.csv',
    'Cryogenic diode measurements': 'python-app/data/external/cryogenic_diode_measurements.csv',
    'Classified combined measurements': 'python-app/data/processed/classified_diode_measurements.csv',
    'External measurements review': 'python-app/data/processed/external_iv_measurements_review.csv',
    'Original cleaned 1N4004': 'python-app/diode_iv_data.csv',
  };
  const METRICS = [
    { Model: 'Random Forest', 'MAE (A)': 0.0001714702, 'RMSE (A)': 0.0004224828, 'R²': 0.9989055 },
    { Model: 'Tuned SVR', 'MAE (A)': 0.0002631377, 'RMSE (A)': 0.0003458506, 'R²': 0.9992665 },
    { Model: 'Linear Regression', 'MAE (A)': 0.006944, 'RMSE (A)': 0.009559, 'R²': 0.439677 },
    { Model: 'Mean baseline', 'MAE (A)': 0.008777, 'RMSE (A)': 0.012815, 'R²': -0.007052 },
  ];
  const MODEL_NAMES = [
    'Random Forest', 'Tuned SVR', 'Silicon SVR', 'SiC SVR',
    'Silicon multi-temperature SVR', 'SiC multi-temperature SVR',
    '1N4004 Reverse-bias SVR',
  ];
  const TRAINED_SILICON_DEVICES = [
    '1N11877R', '1N1190', '1N3913', '45L120', 'BYX661000',
    'BZW12360', 'BZW1336', 'BZW1347', 'MBR4035',
  ];
  const cache = new Map();
  const state = {
    page: 'Home', models: null, data: [], training: [],
    lastPrediction: null, curveSelections: null,
    guideDevice: null, guideTemperature: null,
    datasetFrame: null, comparisonFamily: '1N4004',
  };

  const $ = (id) => document.getElementById(id);
  const finite = (value) => Number.isFinite(Number(value));
  const num = (value) => {
    if (value === null || value === undefined || value === '') return NaN;
    const n = Number(value);
    return Number.isFinite(n) ? n : NaN;
  };
  const unique = (arr) => [...new Set(arr)];
  const sortedUnique = (arr) => unique(arr.filter((x) => x !== null && x !== undefined && x !== '').map(String)).sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  const fmt = (x, digits = 6) => Number(x).toLocaleString('en-US', { maximumSignificantDigits: digits });
  const fmtFixed = (x, digits = 3) => Number(x).toFixed(digits);
  const esc = (value) => String(value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const setHidden = (el, hidden) => { if (el) el.hidden = !!hidden; };

  async function fetchText(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`${path} could not be loaded (${response.status})`);
    return response.text();
  }

  async function readCsv(path) {
    if (cache.has(path)) return cache.get(path);
    const promise = (async () => {
      const text = await fetchText(path);
      if (window.Papa) {
        const parsed = Papa.parse(text, { header: true, skipEmptyLines: true, dynamicTyping: false });
        if (parsed.errors?.length && !parsed.data.length) throw new Error(parsed.errors[0].message);
        return parsed.data;
      }
      return parseCsvFallback(text);
    })();
    cache.set(path, promise);
    try { const rows = await promise; cache.set(path, rows); return rows; } catch (error) { cache.delete(path); throw error; }
  }

  function parseCsvFallback(text) {
    const rows = [];
    let row = [], field = '', quoted = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (quoted) {
        if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
        else if (c === '"') quoted = false;
        else field += c;
      } else if (c === '"') quoted = true;
      else if (c === ',') { row.push(field); field = ''; }
      else if (c === '\n') { row.push(field.replace(/\r$/, '')); rows.push(row); row = []; field = ''; }
      else field += c;
    }
    row.push(field.replace(/\r$/, '')); if (row.length > 1 || row[0] !== '') rows.push(row);
    const headers = rows.shift() || [];
    return rows.map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ''])));
  }

  function parseNumberFields(rows, fields) {
    return rows.map((row) => {
      const out = { ...row };
      fields.forEach((field) => { if (field in out) out[field] = num(out[field]); });
      return out;
    });
  }

  function sortByNumeric(rows, field) {
    return [...rows].sort((a, b) => num(a[field]) - num(b[field]));
  }

  function setPage(page) {
    if (!PAGES.some(([name]) => name === page)) return;
    state.page = page;
    PAGES.forEach(([name, id]) => $(id).classList.toggle('active', name === page));
    document.querySelectorAll('.nav-button').forEach((button) => button.classList.toggle('active', button.dataset.page === page));
    if (page === 'Project Guide') renderGuideChart();
    if (page === 'Predictor') refreshPredictor();
    if (page === 'Model Comparison') renderComparison();
    if (page === 'Dataset Explorer') renderDataset();
    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  function voltageCurrentColumns(frame) {
    const pairs = [
      ['v_meas', 'i_meas'], ['voltage_V', 'current_A'], ['V_V', 'I_A'],
      ['V', 'I'], ['voltage', 'current'],
    ];
    for (const [v, i] of pairs) if (frame.length && v in frame[0] && i in frame[0]) return [v, i];
    return [null, null];
  }

  function materialRows(material) {
    return state.training.filter((r) => String(r.material).trim().toLowerCase() === material);
  }
  function deviceRows(material, device) {
    return materialRows(material).filter((r) => String(r.device) === String(device));
  }
  function temperatures(rows) { return [...new Set(rows.map((r) => num(r.temperature_K)).filter(Number.isFinite))].sort((a, b) => a - b); }
  function nearestIndex(values, target) {
    if (!values.length) return 0;
    let best = 0;
    for (let i = 1; i < values.length; i++) if (Math.abs(values[i] - target) < Math.abs(values[best] - target)) best = i;
    return best;
  }
  function filterGaN(frame) {
    if (!frame.length) return frame;
    const columns = ['material', 'device', 'technology'].filter((c) => c in frame[0]);
    if (!columns.length) return frame;
    return frame.filter((row) => !columns.some((column) => /\bgan\b|gallium nitride/i.test(String(row[column] ?? ''))));
  }

  async function init() {
    document.querySelectorAll('[data-page]').forEach((el) => el.addEventListener('click', () => setPage(el.dataset.page)));
    document.querySelectorAll('[data-go]').forEach((el) => el.addEventListener('click', () => setPage(el.dataset.go)));
    bindControls();
    try {
      const [models, rawData, rawTraining] = await Promise.all([
        fetch('./assets/browser-models.json').then((r) => { if (!r.ok) throw new Error('Browser model export is missing.'); return r.json(); }),
        readCsv('python-app/diode_iv_data.csv'),
        readCsv('python-app/data/processed/classified_diode_measurements.csv'),
      ]);
      state.models = models;
      state.data = sortByNumeric(parseNumberFields(rawData, ['v_meas', 'i_meas']).filter((r) => finite(r.v_meas) && finite(r.i_meas)), 'v_meas');
      state.training = parseNumberFields(filterGaN(rawTraining), ['voltage_V', 'current_A', 'temperature_K'])
        .filter((r) => r.device && r.material && finite(r.voltage_V) && finite(r.current_A) && finite(r.temperature_K));
      if (Object.keys(models.models || {}).length !== 7) throw new Error(`Expected 7 exported models; found ${Object.keys(models.models || {}).length}.`);
      $('global-status').textContent = 'All saved models loaded successfully.';
      setHidden($('global-status'), false);
      updateHomeMetrics();
      renderGuideMetrics();
      initializeGuideSelectors();
      initializePredictor();
      initializeComparison();
      initializeDatasetSelector();
      setPage('Home');
    } catch (error) {
      setHidden($('global-status'), true);
      $('global-error').textContent = `Application data could not be loaded: ${error.message}. Run this site from GitHub Pages or a local HTTP server, not by opening the HTML file directly.`;
      setHidden($('global-error'), false);
      setHidden($('predictor-unavailable'), false);
      console.error(error);
    }
  }

  function bindControls() {
    $('predict-device-type').addEventListener('change', () => { rebuildPredictorSelectors(); renderPredictorWarnings(); renderCurveCheckboxes(true); renderPredictorGraph(); refreshPredictionResult(); });
    $('predict-device').addEventListener('change', () => { rebuildPredictorTemperature(); renderPredictorWarnings(); renderCurveCheckboxes(true); renderPredictorGraph(); refreshPredictionResult(); });
    $('predict-model').addEventListener('change', () => { renderPredictorWarnings(); refreshPredictionResult(); renderPredictorGraph(); });
    $('predict-temperature').addEventListener('change', () => { renderPredictorWarnings(); refreshPredictionResult(); renderPredictorGraph(); });
    $('predict-voltage').addEventListener('input', () => { renderPredictorWarnings(); refreshPredictionResult(); renderPredictorGraph(); });
    $('predict-button').addEventListener('click', predictCurrent);
    $('iv-graph-view').addEventListener('change', renderGraphViewControls);
    $('comparison-family').addEventListener('change', () => { state.comparisonFamily = $('comparison-family').value; renderComparison(); });
    $('comparison-1n-model').addEventListener('change', render1nComparisonPlot);
    $('comparison-device').addEventListener('change', () => { rebuildComparisonTemperatures(); renderMaterialComparisonPlot(); });
    $('comparison-temperature').addEventListener('change', renderMaterialComparisonPlot);
    $('comparison-model').addEventListener('change', renderMaterialComparisonPlot);
    $('dataset-select').addEventListener('change', renderDataset);
    $('guide-device').addEventListener('change', () => { rebuildGuideTemperatures(); renderGuideChart(); });
    $('guide-temperature').addEventListener('change', renderGuideChart);
  }

  function updateHomeMetrics() {
    const valid = state.data.length > 0;
    const vmin = valid ? Math.min(...state.data.map((r) => r.v_meas)) : 0;
    const vmax = valid ? Math.max(...state.data.map((r) => r.v_meas)) : 0.815;
    const displayMin = Math.abs(vmin) < 0.0005 ? 0 : vmin;
    const displayMax = Math.abs(vmax) < 0.0005 ? 0 : vmax;
    $('home-observations').textContent = valid ? String(state.data.length) : '—';
    $('home-voltage-min').textContent = `${displayMin.toFixed(3)} V`;
    $('home-voltage-span').textContent = `to ${displayMax.toFixed(3)} V in the 1N4004 data`;
    $('home-model-count').textContent = String(Object.keys(state.models.models).length);
    $('home-material-observations').textContent = state.training.length.toLocaleString('en-US');
  }

  function renderGuideMetrics() {
    $('guide-1n-count').textContent = state.data.length.toLocaleString('en-US');
    $('guide-classified-count').textContent = state.training.length.toLocaleString('en-US');
    $('guide-device-count').textContent = unique(state.training.map((r) => String(r.device))).length.toLocaleString('en-US');
    $('guide-data-caption').textContent = `The classified file used by the app contains ${state.training.length.toLocaleString('en-US')} complete rows across ${unique(state.training.map((r) => String(r.device))).length} devices in silicon and silicon carbide. The available measured temperatures in this file are 77 K and 293 K. Individual devices may have only these two measured temperature conditions; the app does not invent intermediate measurements.`;
  }

  function renderGuideMetricsTable() {
    const tbody = $('guide-metrics-table').querySelector('tbody');
    tbody.innerHTML = METRICS.map((r) => `<tr><td>${esc(r.Model)}</td><td>${r['MAE (A)']}</td><td>${r['RMSE (A)']}</td><td>${r['R²']}</td></tr>`).join('');
  }

  function initializeGuideSelectors() {
    renderGuideMetricsTable();
    const devices = sortedUnique(state.training.map((r) => String(r.device)));
    fillSelect($('guide-device'), devices);
    if (!state.guideDevice || !devices.includes(state.guideDevice)) state.guideDevice = devices[0] || '';
    $('guide-device').value = state.guideDevice;
    rebuildGuideTemperatures();
  }
  function rebuildGuideTemperatures() {
    state.guideDevice = $('guide-device').value;
    const rows = state.training.filter((r) => String(r.device) === state.guideDevice);
    const temps = temperatures(rows);
    fillSelect($('guide-temperature'), temps.map(String));
    if (!temps.includes(Number(state.guideTemperature))) state.guideTemperature = temps[nearestIndex(temps, 293)] ?? null;
    $('guide-temperature').value = state.guideTemperature === null ? '' : String(state.guideTemperature);
    renderGuideChart();
  }
  function renderGuideChart() {
    if (!window.Plotly) return;
    const device = $('guide-device').value;
    const temp = num($('guide-temperature').value);
    const rows = sortByNumeric(state.training.filter((r) => String(r.device) === String(device) && num(r.temperature_K) === temp && finite(r.voltage_V) && finite(r.current_A)), 'voltage_V');
    // Display the selected device and its measured temperature.
    $('guide-measured-caption').textContent = `${rows.length} measured points for ${device} at ${fmt(temp)} K.`;
    Plotly.react('guide-chart', [{ x: rows.map((r) => r.voltage_V), y: rows.map((r) => r.current_A), type: 'scatter', mode: 'lines', line: { width: 2 }, name: 'Measured current' }], darkLayout({ xaxis: { title: 'Voltage (V)' }, yaxis: { title: 'Current (A)' }, height: 380 }), { responsive: true, displaylogo: false });
  }

  function fillSelect(select, values) {
    const old = select.value;
    select.innerHTML = values.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
    if (values.map(String).includes(old)) select.value = old;
  }

  function refreshPredictor() {
    renderPredictorWarnings();
    refreshPredictionResult();
    renderCurveCheckboxes(false);
    renderPredictorGraph();
  }

  function initializePredictor() {
    rebuildPredictorSelectors();
    renderCurveCheckboxes(true);
    renderGraphViewControls();
  }
  function getPredictorContext() {
    const type = $('predict-device-type').value;
    const material = type === 'Silicon' ? 'silicon' : type === 'Silicon carbide (SiC)' ? 'silicon carbide' : null;
    let device = '1N4004';
    let rows = [];
    if (material) { device = $('predict-device').value; rows = deviceRows(material, device); }
    const model = $('predict-model').value;
    const temperature = material ? num($('predict-temperature').value) : 293;
    const voltage = num($('predict-voltage').value);
    return { type, material, device, rows, model, temperature, voltage };
  }
  function rebuildPredictorSelectors() {
    const type = $('predict-device-type').value;
    const material = type === 'Silicon' ? 'silicon' : type === 'Silicon carbide (SiC)' ? 'silicon carbide' : null;
    if (!material) {
      setHidden($('predict-device-wrap'), true);
      setHidden($('predict-temperature-wrap'), true);
      fillSelect($('predict-model'), ['Random Forest', 'Tuned SVR', '1N4004 Reverse-bias SVR'].filter((n) => state.models.models[n]));
      $('predict-model-wrap').querySelector('label');
      $('predict-model-wrap').firstChild && ($('predict-model-wrap').firstChild.textContent = '2. Choose model');
    } else {
      const materialRows = materialRowsSafe(material);
      const available = unique(materialRows.map((r) => String(r.device)).filter(Boolean));
      const allowed = type === 'Silicon' ? available.filter((d) => TRAINED_SILICON_DEVICES.includes(d)).sort() : available.sort();
      setHidden($('predict-device-wrap'), false);
      setHidden($('predict-temperature-wrap'), false);
      fillSelect($('predict-device'), allowed);
      $('predict-device-wrap').querySelector('label');
      $('predict-device-wrap').firstChild && ($('predict-device-wrap').firstChild.textContent = '2. Choose device');
      const modelNames = type === 'Silicon' ? ['Silicon multi-temperature SVR', 'Silicon SVR'] : ['SiC multi-temperature SVR', 'SiC SVR'];
      fillSelect($('predict-model'), modelNames.filter((n) => state.models.models[n]));
      $('predict-model-wrap').firstChild && ($('predict-model-wrap').firstChild.textContent = '3. Choose model');
      if (!allowed.length) addAlert('predictor-alerts', `No ${type} devices were found in the combined dataset.`, 'warning');
      rebuildPredictorTemperature();
    }
    $('predict-model').value = $('predict-model').options[0]?.value || '';
    renderPredictorWarnings();
  }
  function materialRowsSafe(material) { return materialRows(material); }
  function rebuildPredictorTemperature() {
    const type = $('predict-device-type').value;
    if (type === '1N4004') return;
    const material = type === 'Silicon' ? 'silicon' : 'silicon carbide';
    const rows = deviceRows(material, $('predict-device').value);
    const temps = temperatures(rows);
    const old = num($('predict-temperature').value);
    fillSelect($('predict-temperature'), temps.map(String));
    if (temps.length) $('predict-temperature').value = String(temps[nearestIndex(temps, Number.isFinite(old) ? old : 293)]);
  }

  function addAlert(containerId, message, kind = 'info') {
    const el = document.createElement('div');
    el.className = `alert alert-${kind}`;
    el.textContent = message;
    $(containerId).appendChild(el);
  }
  function currentOneNRange(voltage) {
    const key = voltage < 0 ? '1N4004 reverse bias' : '1N4004 forward bias';
    return readCsv(DATASET_FILES[key]).then((frame) => {
      const [vCol] = voltageCurrentColumns(frame);
      const vals = frame.map((r) => num(r[vCol])).filter(Number.isFinite);
      return vals.length ? { min: Math.min(...vals), max: Math.max(...vals), key } : { min: null, max: null, key };
    });
  }
  async function renderPredictorWarnings() {
    const c = getPredictorContext();
    const holder = $('predictor-alerts'); holder.innerHTML = '';
    if (!c.model || !state.models) return;
    if (c.type !== '1N4004' && c.device && c.rows.length) {
      const rows = c.rows.filter((r) => num(r.temperature_K) === c.temperature);
      if (rows.length) {
        const values = rows.map((r) => num(r.voltage_V)).filter(Number.isFinite);
        const min = Math.min(...values), max = Math.max(...values);
        const p = document.createElement('p'); p.className = 'caption'; p.textContent = `Recorded voltage range for ${c.device} at ${fmt(c.temperature)} K: ${fmt(min,5)} to ${fmt(max,5)} V.`; holder.appendChild(p);
        if (c.voltage < min || c.voltage > max) addAlert('predictor-alerts', 'The voltage is outside this device\'s recorded range; the prediction may be unreliable.', 'warning');
      } else addAlert('predictor-alerts', `No measured temperatures were found for this device.`, 'warning');
    } else if (c.type === '1N4004' && Number.isFinite(c.voltage)) {
      try {
        const range = await currentOneNRange(c.voltage);
        if (range.min !== null && (c.voltage < range.min || c.voltage > range.max)) {
          addAlert('predictor-alerts', `The voltage is outside the 1N4004 ${range.key} measured range (${fmt(range.min,5)} to ${fmt(range.max,5)} V). The prediction may be unreliable.`, 'warning');
        } else if (range.min === null) addAlert('predictor-alerts', `Could not load the matching 1N4004 ${range.key} voltage range.`, 'warning');
      } catch (e) { addAlert('predictor-alerts', `Could not load the matching 1N4004 measured voltage range: ${e.message}`, 'warning'); }
    }
    if (c.type === '1N4004') {
      if (c.model === '1N4004 Reverse-bias SVR') {
        if (c.voltage > 0) addAlert('predictor-alerts', 'Forward bias: the selected 1N4004 model was trained using reverse-bias measurements. Its forward-current prediction is not validated. Select Random Forest or Tuned SVR instead.', 'warning');
        else if (c.voltage < 0) addAlert('predictor-alerts', 'Reverse bias: the selected model was trained using 1N4004 reverse-bias measurements. Its predictions are still estimates.', 'info');
      } else if (c.voltage < 0) addAlert('predictor-alerts', 'Reverse bias: the selected 1N4004 model was trained using forward-bias measurements. Its reverse-current prediction is not validated. Select the 1N4004 Reverse-bias SVR instead.', 'warning');
    } else if (c.voltage < 0) {
      addAlert('predictor-alerts', 'Reverse bias: the available measurements for this material contain no negative-voltage data. The selected model is not validated for reverse-bias predictions.', 'warning');
    }
  }

  function predictionMatches(context) {
    const r = state.lastPrediction;
    return !!r && r.model === context.model && r.device === context.device && r.voltage === context.voltage && r.temperature === context.temperature && Number.isFinite(Number(r.current));
  }
  function refreshPredictionResult() {
    const c = getPredictorContext();
    const holder = $('prediction-result');
    if (!predictionMatches(c)) { holder.innerHTML = ''; setHidden(holder, true); return; }
    renderPredictionResult(state.lastPrediction);
  }
  function renderPredictionResult(result) {
    const holder = $('prediction-result');
    holder.innerHTML = `
      <h3>Prediction result</h3>
      <div class="result-grid">
        <div class="result-card"><div class="result-label">Predicted current</div><div class="result-value">${fmt(result.current)} A</div></div>
        <div class="result-card"><div class="result-label">Equivalent current</div><div class="result-value">${fmt(result.current * 1000)} mA</div></div>
        <div class="result-card"><div class="result-label">Model</div><div class="result-value">${esc(result.model)}</div></div>
      </div>
      <div id="prediction-result-note"></div>
      <details class="details-panel"><summary>How should I interpret this prediction?</summary>
        <p>Model: ${esc(result.model)}</p><p>Device: ${esc(result.device)}</p><p>Voltage: ${Number(result.voltage).toFixed(5)} V</p><p>Temperature: ${fmt(result.temperature)} K</p>
        <p>Estimated current: ${fmt(result.current)} A (${fmt(result.current * 1000)} mA)</p>
        <p>A prediction inside the measured voltage range can still be inaccurate. These models are estimates, not substitutes for physical measurements.</p>
      </details>`;
    setHidden(holder, false);
    const note = $('prediction-result-note');
    if (['Silicon SVR', 'SiC SVR', 'Silicon multi-temperature SVR', 'SiC multi-temperature SVR'].includes(result.model)) {
      note.className = 'alert alert-info';
      note.textContent = `Estimate for ${result.device} at ${fmt(result.temperature)} K. The voltage is within the measured range for this device and temperature, but the estimate is not a guaranteed physical measurement.`;
    } else if (result.device === '1N4004') {
      currentOneNRange(result.voltage).then((range) => {
        if (range.min !== null && !(range.min <= result.voltage && result.voltage <= range.max)) {
          note.className = 'alert alert-warning'; note.textContent = `${Number(result.voltage).toFixed(5)} V is outside the 1N4004 ${range.key} measured range (${range.min.toFixed(5)}–${range.max.toFixed(5)} V). Treat this prediction as an extrapolation.`;
        } else if (result.voltage < 0) {
          note.className = 'alert alert-warning';
          note.textContent = result.model === '1N4004 Reverse-bias SVR'
            ? 'This estimate uses the 1N4004 reverse-bias model. It is based on measured reverse-bias data, but its accuracy is limited and it should not be treated as a guaranteed physical measurement.'
            : 'The selected model was trained on forward-bias data only. Its reverse-current prediction is not validated.';
        } else { note.className = 'alert alert-info'; note.textContent = 'This is a model estimate, not a guaranteed physical measurement.'; }
      }).catch(() => { note.className = 'alert alert-info'; note.textContent = 'This is a model estimate, not a guaranteed physical measurement.'; });
    } else { note.className = 'alert alert-info'; note.textContent = 'This is a model estimate, not a guaranteed physical measurement.'; }
  }

  function predictCurrent() {
    const c = getPredictorContext();
    state.lastPrediction = null;
    refreshPredictionResult();
    if (!c.model || !Number.isFinite(c.voltage)) return;
    try {
      let current;
      if (['Silicon SVR', 'SiC SVR', 'Silicon multi-temperature SVR', 'SiC multi-temperature SVR'].includes(c.model)) {
        const deviceData = state.training.filter((r) => String(r.device) === String(c.device) && num(r.temperature_K) === c.temperature && num(r.current_A) > 0);
        if (!deviceData.length) { addAlert('predictor-alerts', `No measured data is available for ${c.device} at exactly ${fmt(c.temperature)} K. Choose a temperature with measured data.`, 'error'); return; }
        const input = { device: c.device, voltage_V: c.voltage, temperature_K: c.temperature };
        current = window.DiodeLabModels.predictCurrent(state.models, c.model, input);
      } else if (c.model === '1N4004 Reverse-bias SVR') {
        current = window.DiodeLabModels.predictCurrent(state.models, c.model, { v_meas: c.voltage });
        if (!Number.isFinite(current) || current <= 0) { addAlert('predictor-alerts', 'The reverse-bias model returned an invalid prediction.', 'error'); return; }
      } else {
        current = window.DiodeLabModels.predictRaw(state.models, c.model, { v_meas: c.voltage });
        if (!Number.isFinite(current)) { addAlert('predictor-alerts', 'The model returned a non-finite prediction.', 'error'); return; }
      }
      state.lastPrediction = { model: c.model, device: c.device, voltage: c.voltage, temperature: c.temperature, current };
      renderPredictionResult(state.lastPrediction);
      renderPredictorGraph();
    } catch (error) {
      addAlert('predictor-alerts', `Prediction failed: ${error.message}`, 'error');
      state.lastPrediction = null;
    }
  }

  function comparisonOptions() {
    const c = getPredictorContext();
    const options = [
      { label: '1N4004 forward bias', type: 'dataset', value: '1N4004 forward bias' },
      { label: '1N4004 reverse bias', type: 'dataset', value: '1N4004 reverse bias' },
    ];
    if (state.training.length) {
      const seen = new Set();
      for (const row of state.training) {
        const dev = String(row.device), mat = String(row.material);
        if (c.type !== '1N4004' && dev === String(c.device)) continue;
        const label = `${dev} (${mat})`;
        if (!seen.has(label)) { seen.add(label); options.push({ label, type: 'device', value: dev }); }
      }
    }
    return options;
  }
  function renderCurveCheckboxes(reset = false) {
    const holder = $('curve-checkboxes');
    const options = comparisonOptions();
    if (!state.curveSelections || reset) {
      if (!state.curveSelections) {
        state.curveSelections = new Set();
        const v = num($('predict-voltage').value);
        state.curveSelections.add(v >= 0 ? 'dataset:1N4004 forward bias' : 'dataset:1N4004 reverse bias');
      }
      // Retain user selection for existing options; only remove a device no longer present.
      const allowed = new Set(options.map((o) => `${o.type}:${o.value}`));
      state.curveSelections = new Set([...state.curveSelections].filter((x) => allowed.has(x) || x.startsWith('dataset:')));
    }
    holder.innerHTML = options.map((o) => {
      const key = `${o.type}:${o.value}`;
      return `<label class="checkbox-item"><input type="checkbox" data-curve-key="${esc(key)}" ${state.curveSelections.has(key) ? 'checked' : ''}><span>${esc(o.label)}</span></label>`;
    }).join('');
    holder.querySelectorAll('input').forEach((checkbox) => checkbox.addEventListener('change', () => {
      const key = checkbox.dataset.curveKey;
      checkbox.checked ? state.curveSelections.add(key) : state.curveSelections.delete(key);
      renderPredictorGraph();
    }));
  }

  function renderGraphViewControls() {
    const mode = $('iv-graph-view').value;
    const holder = $('graph-view-controls');
    if (mode === 'Zoom around selected voltage') {
      holder.innerHTML = '<label class="standalone-control">Voltage window width (V)<input id="iv-zoom-width" type="range" min="0.01" max="10" step="0.01" value="0.5"><span id="iv-zoom-value" class="caption">0.50 V</span></label>';
      $('iv-zoom-width').addEventListener('input', () => { $('iv-zoom-value').textContent = `${Number($('iv-zoom-width').value).toFixed(2)} V`; renderPredictorGraph(); });
    } else if (mode === 'Custom voltage range') {
      const v = allGraphVoltages();
      const min = v.length ? Math.min(...v) : -1, max = v.length ? Math.max(...v) : 1;
      holder.innerHTML = `<div class="range-inputs"><label>Minimum visible voltage (V)<input id="iv-custom-min" type="number" step="any" value="${min}"></label><label>Maximum visible voltage (V)<input id="iv-custom-max" type="number" step="any" value="${max}"></label></div>`;
      ['iv-custom-min', 'iv-custom-max'].forEach((id) => $(id).addEventListener('input', renderPredictorGraph));
    } else holder.innerHTML = '';
    renderPredictorGraph();
  }

  function allGraphVoltages() {
    const c = getPredictorContext();
    let volts = [];
    if (c.type !== '1N4004' && c.device) {
      const filtered = c.rows.filter((r) => num(r.temperature_K) === c.temperature);
      volts.push(...filtered.map((r) => num(r.voltage_V)).filter(Number.isFinite));
    }
    for (const key of state.curveSelections || []) {
      const [type, ...rest] = key.split(':');
      const value = rest.join(':');
      if (type === 'dataset' && DATASET_FILES[value]) {
        // Range is completed by the full curve loader. Keep current known graph points here.
        const loaded = cache.get(DATASET_FILES[value]);
        if (loaded && typeof loaded.then === 'undefined') {
          const [vc] = voltageCurrentColumns(loaded);
          if (vc) volts.push(...loaded.map((r) => num(r[vc])).filter(Number.isFinite));
        }
      }
    }
    if (predictionMatches(c)) volts.push(c.voltage);
    return volts;
  }

  async function buildCurveData() {
    const c = getPredictorContext();
    const curves = [];
    if (c.type !== '1N4004' && c.device && c.rows.length) {
      const rows = c.rows.filter((r) => num(r.temperature_K) === c.temperature);
      const curve = rows.map((r) => ({ voltage: num(r.voltage_V), current: num(r.current_A) })).filter((r) => Number.isFinite(r.voltage) && Number.isFinite(r.current)).sort((a, b) => a.voltage - b.voltage);
      if (curve.length) curves.push({ label: `Selected device: ${c.device} (${fmt(c.temperature)} K)`, points: curve });
    }
    const opts = comparisonOptions();
    for (const key of state.curveSelections || []) {
      const [type, ...rest] = key.split(':'); const value = rest.join(':');
      const opt = opts.find((o) => o.type === type && o.value === value);
      if (!opt) continue;
      if (type === 'dataset') {
        try {
          const frame = await readCsv(DATASET_FILES[value]);
          const [vCol, iCol] = voltageCurrentColumns(frame);
          if (!vCol) continue;
          const points = frame.map((r) => ({ voltage: num(r[vCol]), current: num(r[iCol]) })).filter((r) => Number.isFinite(r.voltage) && Number.isFinite(r.current)).sort((a, b) => a.voltage - b.voltage);
          if (points.length) curves.push({ label: opt.label, points });
        } catch (e) { console.warn(e); }
      } else {
        const rows = state.training.filter((r) => String(r.device) === value);
        const temps = temperatures(rows);
        if (!temps.length) continue;
        const nearest = temps[nearestIndex(temps, c.temperature)];
        const points = rows.filter((r) => num(r.temperature_K) === nearest).map((r) => ({ voltage: num(r.voltage_V), current: num(r.current_A) })).filter((r) => Number.isFinite(r.voltage) && Number.isFinite(r.current)).sort((a, b) => a.voltage - b.voltage);
        if (points.length) curves.push({ label: `${opt.label} (${fmt(nearest)} K)`, points });
      }
    }
    return curves;
  }

  async function renderPredictorGraph() {
    if (!window.Plotly || !state.models) return;
    const c = getPredictorContext();
    const curves = await buildCurveData();
    const matchingResult = predictionMatches(c);
    const allVoltages = curves.flatMap((curve) => curve.points.map((p) => p.voltage));
    if (matchingResult) allVoltages.push(c.voltage);
    let dataMin = allVoltages.length ? Math.min(...allVoltages) : -1;
    let dataMax = allVoltages.length ? Math.max(...allVoltages) : 1;
    if (dataMin === dataMax) { dataMin -= .1; dataMax += .1; }
    let xRange;
    let customRangeInvalid = false;
    const mode = $('iv-graph-view').value;
    if (mode === 'Full voltage range') xRange = [dataMin, dataMax];
    else if (mode === 'Forward bias (0 V and above)') {
      const positive = allVoltages.filter((v) => v >= 0); xRange = positive.length ? [0, Math.max(...positive)] : [0, 1]; if (xRange[0] === xRange[1]) xRange[1] += .1;
    } else if (mode === 'Reverse bias (below 0 V)') {
      const negative = allVoltages.filter((v) => v < 0); xRange = negative.length ? [Math.min(...negative), 0] : [-1, 0];
    } else if (mode === 'Zoom around selected voltage') {
      const width = num($('iv-zoom-width')?.value ?? .5); xRange = [c.voltage - width / 2, c.voltage + width / 2];
    } else {
      const xmin = num($('iv-custom-min')?.value ?? dataMin); const xmax = num($('iv-custom-max')?.value ?? dataMax);
      if (xmin >= xmax) { customRangeInvalid = true; xRange = [dataMin, dataMax]; }
      else { setHidden($('predictor-graph-note'), true); xRange = [xmin, xmax]; }
    }
    const linthresh = 1e-9;
    const symlog = (v) => Math.sign(v) * Math.log10(1 + Math.abs(v) / linthresh);
    const traces = curves.map((curve) => ({
      x: curve.points.map((p) => p.voltage), y: curve.points.map((p) => symlog(p.current)),
      customdata: curve.points.map((p) => p.current), type: 'scatter', mode: 'lines+markers', name: curve.label,
      line: { width: 2 }, marker: { size: 4 },
      hovertemplate: 'Voltage: %{x:.6g} V<br>Current: %{customdata:.6g} A<extra>%{fullData.name}</extra>',
    }));
    if (matchingResult) traces.push({
      x: [c.voltage], y: [symlog(state.lastPrediction.current)], customdata: [state.lastPrediction.current], type: 'scatter', mode: 'markers', name: 'Predicted current',
      marker: { symbol: 'star', size: 18, color: '#ffcc66', line: { color: 'white', width: 1.5 } },
      hovertemplate: '<b>MODEL PREDICTION</b><br>Voltage: %{x:.6g} V<br>Predicted current: %{customdata:.6g} A<extra></extra>',
    });
    const tickCurrents = [-1,-.1,-.01,-.001,-1e-4,-1e-5,-1e-6,-1e-7,-1e-8,-1e-9,0,1e-9,1e-8,1e-7,1e-6,1e-5,1e-4,.001,.01,.1,1];
    const layout = darkLayout({
      title: 'Diode I–V characteristics', height: 650, autosize: true,
      margin: { l: 85, r: 30, t: 75, b: 100 }, hovermode: 'closest',
      legend: { bgcolor: 'rgba(16,34,59,0.9)', bordercolor: '#294563', borderwidth: 1 },
      xaxis: { title: 'Voltage (V) — negative: reverse bias; positive: forward bias', range: xRange, showgrid: true, gridcolor: 'rgba(82,112,142,0.3)', zeroline: true, zerolinecolor: '#7890ad', automargin: true },
      yaxis: { title: 'Current (A, symmetric-log scale)', tickmode: 'array', tickvals: tickCurrents.map(symlog), ticktext: tickCurrents.map((v) => v ? v.toExponential(0) : '0'), showgrid: true, gridcolor: 'rgba(82,112,142,0.3)', zeroline: true, zerolinecolor: '#7890ad', automargin: true },
      shapes: [{ type: 'line', x0: c.voltage, x1: c.voltage, y0: 0, y1: 1, yref: 'paper', line: { color: '#9dbcf4', width: 1.3, dash: 'dash' } }],
      annotations: [{ x: c.voltage, y: 1, yref: 'paper', text: `Selected: ${fmt(c.voltage, 4)} V`, showarrow: false, yanchor: 'bottom', font: { color: '#c7d7ec', size: 11 } }],
    });
    if (customRangeInvalid) { $('predictor-graph-note').textContent = 'The maximum voltage must be greater than the minimum voltage.'; setHidden($('predictor-graph-note'), false); }
    else if (!curves.length && !matchingResult) { $('predictor-graph-note').textContent = 'Select one or more datasets above to display curves. The prediction marker appears after a successful prediction.'; setHidden($('predictor-graph-note'), false); }
    else setHidden($('predictor-graph-note'), true);
    await Plotly.react('predictor-graph', traces, layout, { scrollZoom: true, displaylogo: false, responsive: true });
  }

  function darkLayout(extra = {}) {
    return Object.assign({
      template: 'plotly_dark', paper_bgcolor: '#081326', plot_bgcolor: '#081326',
      font: { family: 'Inter, sans-serif', color: '#a9c4df' },
      margin: { l: 64, r: 24, t: 55, b: 60 }, autosize: true,
      xaxis: { gridcolor: 'rgba(82,112,142,0.3)', zerolinecolor: '#7890ad', automargin: true },
      yaxis: { gridcolor: 'rgba(82,112,142,0.3)', zerolinecolor: '#7890ad', automargin: true },
    }, extra);
  }

  function initializeComparison() {
    $('comparison-family').value = '1N4004';
    fillSelect($('comparison-1n-model'), ['Random Forest', 'Tuned SVR', '1N4004 Reverse-bias SVR'].filter((n) => state.models.models[n]));
    renderComparison();
  }
  function renderComparison() {
    const family = $('comparison-family').value;
    state.comparisonFamily = family;
    const isOneN = family === '1N4004';
    setHidden($('comparison-1n'), !isOneN); setHidden($('comparison-material'), isOneN);
    if (isOneN) {
      renderMetricsTable($('comparison-metrics-table'));
      renderMetricBar('mae-chart', 'MAE (A)'); renderMetricBar('rmse-chart', 'RMSE (A)');
      render1nComparisonPlot();
    } else {
      const material = family === 'Silicon' ? 'silicon' : 'silicon carbide';
      const rows = materialRows(material);
      $('comparison-material-title').textContent = `${family} — measured and predicted I–V curve`;
      if (!rows.length) { $('comparison-material-caption').textContent = `No classified ${family} measurements were found in the training dataset.`; $('comparison-material-plot').innerHTML = ''; return; }
      const devices = sortedUnique(rows.map((r) => String(r.device)));
      fillSelect($('comparison-device'), devices);
      const options = family === 'Silicon' ? ['Silicon SVR', 'Silicon multi-temperature SVR'] : ['SiC SVR', 'SiC multi-temperature SVR'];
      fillSelect($('comparison-model'), options.filter((name) => state.models.models[name]));
      rebuildComparisonTemperatures();
      renderMaterialComparisonPlot();
    }
  }
  function renderMetricsTable(table) {
    table.querySelector('tbody').innerHTML = METRICS.map((r) => `<tr><td>${esc(r.Model)}</td><td>${r['MAE (A)']}</td><td>${r['RMSE (A)']}</td><td>${r['R²']}</td></tr>`).join('');
  }
  function renderMetricBar(id, field) {
    if (!window.Plotly) return;
    Plotly.react(id, [{ type: 'bar', x: METRICS.map((r) => r.Model), y: METRICS.map((r) => r[field]), name: field }], darkLayout({ height: 250, margin: { l: 64, r: 16, t: 20, b: 90 }, showlegend: false, xaxis: { tickangle: -16, automargin: true }, yaxis: { title: field, automargin: true } }), { responsive: true, displaylogo: false });
  }
  function render1nComparisonPlot() {
    if (!window.Plotly || !state.models) return;
    const selected = $('comparison-1n-model').value;
    const xs = state.data.length ? Array.from({ length: 350 }, (_, i) => Math.min(...state.data.map((r) => r.v_meas)) + (Math.max(...state.data.map((r) => r.v_meas)) - Math.min(...state.data.map((r) => r.v_meas))) * i / 349) : [];
    const traces = [{ x: state.data.map((r) => r.v_meas), y: state.data.map((r) => r.i_meas), type: 'scatter', mode: 'markers', name: 'Measured data', marker: { size: 6, color: '#62c9ff' } }];
    if (selected && xs.length) {
      const ys = xs.map((v) => window.DiodeLabModels.predictRaw(state.models, selected, { v_meas: v }));
      traces.push({ x: xs, y: ys, type: 'scatter', mode: 'lines', name: `${selected} prediction`, line: { width: 2.5, color: '#ffbd66' } });
    }
    Plotly.react('comparison-1n-plot', traces, darkLayout({ title: '1N4004 forward-bias I–V characteristics', height: 420, xaxis: { title: 'Measured voltage (V)' }, yaxis: { title: 'Measured current (A)' }, legend: { orientation: 'h', y: 1.12 } }), { responsive: true, displaylogo: false });
  }
  function rebuildComparisonTemperatures() {
    const family = $('comparison-family').value;
    const material = family === 'Silicon' ? 'silicon' : 'silicon carbide';
    const rows = deviceRows(material, $('comparison-device').value);
    const temps = temperatures(rows);
    fillSelect($('comparison-temperature'), temps.map(String));
    if (temps.length) $('comparison-temperature').value = String(temps[nearestIndex(temps, 293)]);
  }
  function renderMaterialComparisonPlot() {
    if (!window.Plotly || !state.models) return;
    const family = $('comparison-family').value;
    const material = family === 'Silicon' ? 'silicon' : 'silicon carbide';
    const device = $('comparison-device').value;
    const temperature = num($('comparison-temperature').value);
    const modelName = $('comparison-model').value;
    const rows = deviceRows(material, device).filter((r) => num(r.temperature_K) === temperature && num(r.current_A) > 0 && Number.isFinite(num(r.voltage_V)));
    const measured = sortByNumeric(rows, 'voltage_V');
    if (!measured.length) { $('comparison-material-caption').textContent = 'There are no positive-current measured points to plot at this temperature.'; $('comparison-material-plot').innerHTML = ''; return; }
    const min = Math.min(...measured.map((r) => num(r.voltage_V))), max = Math.max(...measured.map((r) => num(r.voltage_V)));
    const xs = Array.from({ length: 250 }, (_, i) => min + (max - min) * i / 249);
    const ys = xs.map((voltage) => window.DiodeLabModels.predictRaw(state.models, modelName, { device, voltage_V: voltage, temperature_K: temperature }));
    const traces = [
      { x: measured.map((r) => num(r.voltage_V)), y: measured.map((r) => num(r.current_A)), type: 'scatter', mode: 'markers', name: 'Measured data', marker: { size: 6 } },
      { x: xs, y: ys, type: 'scatter', mode: 'lines', name: `${modelName} prediction`, line: { width: 2.5 } },
    ];
    Plotly.react('comparison-material-plot', traces, darkLayout({ title: `${device} · ${fmt(temperature)} K · ${family}`, height: 520, xaxis: { title: 'Voltage (V)' }, yaxis: { type: 'log', title: 'Current (A, log scale)' }, legend: { orientation: 'h', y: 1.12 } }), { responsive: true, displaylogo: false });
    $('comparison-material-caption').textContent = `Measured points: ${measured.length.toLocaleString('en-US')}. Prediction shown only over the measured voltage range (${fmt(min,4)} to ${fmt(max,4)} V).`;
  }

  function initializeDatasetSelector() {
    fillSelect($('dataset-select'), Object.keys(DATASET_FILES));
    renderDataset();
  }
  function rowsToCsv(rows, headers) {
    if (window.Papa) return Papa.unparse({ fields: headers, data: rows.map((r) => headers.map((h) => r[h] ?? '')) });
    const q = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    return [headers.map(q).join(','), ...rows.map((r) => headers.map((h) => q(r[h])).join(','))].join('\n');
  }
  async function renderDataset() {
    if (!$('dataset-select').value) return;
    const name = $('dataset-select').value;
    const path = DATASET_FILES[name];
    setHidden($('dataset-error'), true); setHidden($('dataset-content'), true);
    try {
      const frame = filterGaN(await readCsv(path));
      if (!frame.length) throw new Error('This CSV could not be read or contains no rows.');
      state.datasetFrame = frame;
      const headers = Object.keys(frame[0]);
      $('dataset-summary').innerHTML = `<strong>${esc(name)}</strong> — ${frame.length.toLocaleString('en-US')} rows and ${headers.length} columns.`;
      const table = $('dataset-table');
      table.innerHTML = `<thead><tr>${headers.map((h) => `<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${frame.slice(0,500).map((r) => `<tr>${headers.map((h) => `<td>${esc(r[h] ?? '')}</td>`).join('')}</tr>`).join('')}</tbody>`;
      const download = $('dataset-download');
      const blob = new Blob([rowsToCsv(frame, headers)], { type: 'text/csv;charset=utf-8' });
      if (download.dataset.url) URL.revokeObjectURL(download.dataset.url);
      download.href = URL.createObjectURL(blob); download.dataset.url = download.href;
      download.download = path.split('/').pop();
      const [vCol, iCol] = voltageCurrentColumns(frame);
      if (vCol) {
        const points = frame.map((r) => ({ x: num(r[vCol]), y: num(r[iCol]) })).filter((r) => Number.isFinite(r.x) && Number.isFinite(r.y)).sort((a,b) => a.x-b.x);
        $('dataset-plot-title').innerHTML = '<h3>I–V curve</h3>';
        if (window.Plotly) {
          Plotly.react('dataset-plot', [{ x: points.map((p) => p.x), y: points.map((p) => p.y), type: 'scatter', mode: 'lines+markers', name, marker: { size: 4 }, line: { width: 1.5 } }], darkLayout({ title: `${name}: measured I–V curve`, height: 480, xaxis: { title: 'Voltage (V)' }, yaxis: { title: 'Current (A)' }, legend: { orientation: 'h', y: 1.1 } }), { responsive: true, displaylogo: false });
        } else $('dataset-plot').innerHTML = '<p class="caption">The chart library could not be loaded. The dataset table and download remain available.</p>';
      } else {
        $('dataset-plot-title').innerHTML = '<div class="alert alert-info">This dataset does not contain a recognized voltage/current column pair.</div>';
        $('dataset-plot').innerHTML = '';
      }
      setHidden($('dataset-content'), false);
    } catch (error) { $('dataset-error').textContent = error.message; setHidden($('dataset-error'), false); }
  }

  // Ensure the metric table and initial page state are ready after the DOM is parsed.
  document.addEventListener('DOMContentLoaded', init);
})();
