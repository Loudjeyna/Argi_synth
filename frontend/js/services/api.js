/* SynthAI - Backend API Client with automatic JS simulation fallback */
const ApiService = (function() {
    const API_BASE = 'http://127.0.0.1:8001/api';
    const CACHE_KEY = 'synthai_api_available';

    function isAvailable() {
        if (sessionStorage.getItem(CACHE_KEY) === 'true') return true;
        if (sessionStorage.getItem(CACHE_KEY) === 'false') return false;
        return null; // not yet checked
    }

    function setAvailable(val) {
        sessionStorage.setItem(CACHE_KEY, val ? 'true' : 'false');
    }

    function apiPost(path, body) {
        return fetch(API_BASE + path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        }).then(r => {
            if (!r.ok) return r.json().then(e => { throw new Error(e.detail || 'Request failed'); });
            return r.json();
        });
    }

    function apiGet(path) {
        return fetch(API_BASE + path).then(r => {
            if (!r.ok) return r.json().then(e => { throw new Error(e.detail || 'Request failed'); });
            return r.json();
        });
    }

    function healthCheck() {
        return fetch(API_BASE + '/health', { method: 'GET', signal: AbortSignal.timeout(3000) })
            .then(r => { const ok = r.ok; setAvailable(ok); return ok; })
            .catch(() => { setAvailable(false); return false; });
    }

    function login(username, password) {
        return apiPost('/auth/login', { username, password });
    }

    function register(username, email, password, role) {
        return apiPost('/auth/register', { username, email, password, role });
    }

    function getUsers() {
        return apiGet('/users');
    }

    function trainModel(epochs, batchSize) {
        return apiPost('/model/train', { epochs: epochs || 300, batch_size: batchSize || 256 });
    }

    function modelStatus() {
        return apiGet('/model/status');
    }

    function generateData(numRows) {
        return apiPost('/datasets/generate', { num_rows: numRows || 1000 });
    }

    function getDatasets() {
        return apiGet('/datasets');
    }

    function validateDataset(datasetId) {
        return apiGet('/datasets/validate/' + datasetId);
    }

    function getStats() {
        return apiGet('/stats');
    }

    return {
        isAvailable, healthCheck, setAvailable,
        login, register, getUsers,
        trainModel, modelStatus,
        generateData, getDatasets, validateDataset,
        getStats
    };
})();
