// Sample JavaScript application

// appName = {{ values.project.name | quote }}
const appName = 'DefaultApp';

// apiUrl = {{ values.api.base_url | quote }}
const apiUrl = 'http://localhost:3000';

// enableMetrics = {{ values.features.metrics }}
const enableMetrics = false;

console.log(`Starting ${appName}...`);
console.log(`API URL: ${apiUrl}`);
console.log(`Metrics enabled: ${enableMetrics}`);