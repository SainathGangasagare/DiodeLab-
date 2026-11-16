const fs = require('fs');
const modelSet = JSON.parse(fs.readFileSync('assets/browser-models.json', 'utf8'));
const tests = JSON.parse(fs.readFileSync('evaluation_outputs/browser_model_parity_fixtures.json', 'utf8'));
global.window = global;
require('../assets/model-engine.js');
let maxAbsRaw = 0, maxRelCurrent = 0, failures = [];
for (const test of tests) {
  const gotRaw = global.DiodeLabModels.predictRaw(modelSet, test.name, test.input);
  const gotCurrent = global.DiodeLabModels.predictCurrent(modelSet, test.name, test.input);
  const absRaw = Math.abs(gotRaw - test.expectedRaw);
  const relCurrent = Math.abs(gotCurrent - test.expectedCurrent) / Math.max(Math.abs(test.expectedCurrent), 1e-14);
  maxAbsRaw = Math.max(maxAbsRaw, absRaw);
  maxRelCurrent = Math.max(maxRelCurrent, relCurrent);
  if (absRaw > 1e-9 && relCurrent > 1e-8) failures.push({test,gotRaw,gotCurrent,absRaw,relCurrent});
}
console.log(JSON.stringify({n:tests.length,maxAbsRaw,maxRelCurrent,failures:failures.slice(0,5),failureCount:failures.length},null,2));
if (failures.length) process.exit(1);
