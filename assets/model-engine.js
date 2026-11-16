/* DiodeLab browser-side inference engine. Parameters are exported from the
   unchanged seven .joblib artifacts; app.py remains the source reference. */
(function (global) {
  'use strict';

  function scale(values, scaler) {
    if (!scaler) return values.slice();
    return values.map((v, i) => (Number(v) - scaler.mean[i]) / scaler.scale[i]);
  }

  function buildFeatures(model, input) {
    if (!model.featureOrder || model.featureOrder.length === 1) {
      return scale([Number(input.v_meas)], model.scaler);
    }
    const categoryValues = Array.isArray(model.categories && model.categories[0]) ? model.categories[0] : (model.categories || []);
    const oneHot = categoryValues.map((category) => String(category) === String(input.device) ? 1 : 0);
    const numeric = scale(
      [Number(input.voltage_V), Number(input.temperature_K)],
      model.scaler
    );
    return model.featureOrder[0] === 'device'
      ? oneHot.concat(numeric)
      : numeric.concat(oneHot);
  }

  function predictForest(model, input) {
    const x = [Number(input.v_meas)];
    let total = 0;
    for (const tree of model.trees) {
      let node = 0;
      while (tree.left[node] !== -1) {
        const f = tree.feature[node];
        node = x[f] <= tree.threshold[node] ? tree.left[node] : tree.right[node];
      }
      total += tree.value[node];
    }
    return total / model.trees.length;
  }

  function predictSvr(model, input) {
    const x = buildFeatures(model, input);
    let result = model.intercept;
    for (let i = 0; i < model.supportVectors.length; i++) {
      const sv = model.supportVectors[i];
      let squaredDistance = 0;
      for (let j = 0; j < x.length; j++) {
        const delta = x[j] - sv[j];
        squaredDistance += delta * delta;
      }
      result += model.dualCoefficients[i] * Math.exp(-model.gamma * squaredDistance);
    }
    return result;
  }

  function predictRaw(modelSet, modelName, input) {
    const model = modelSet.models[modelName];
    if (!model) throw new Error('Model not present: ' + modelName);
    if (model.kind === 'randomForest') return predictForest(model, input);
    if (model.kind === 'rbfSvr') {
      const raw = predictSvr(model, input);
      return model.targetTransform === 'pow10' ? Math.pow(10, raw) : raw;
    }
    throw new Error('Unsupported browser model type: ' + model.kind);
  }

  function predictCurrent(modelSet, modelName, input) {
    const raw = predictRaw(modelSet, modelName, input);
    if (modelName === '1N4004 Reverse-bias SVR') return Math.pow(10, raw);
    if (modelName === 'Silicon SVR' || modelName === 'SiC SVR') return Math.pow(10, raw);
    // RF and tuned SVR already predict amperes. Transformed-target material
    // estimators also return amperes because their inverse transform is applied.
    return raw;
  }

  global.DiodeLabModels = {
    predictRaw,
    predictCurrent,
    buildFeatures,
  };
})(window);
