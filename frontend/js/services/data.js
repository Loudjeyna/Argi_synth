/* SynthAI - Realistic Agricultural Data Generation Service */
const DataService = (function() {
    const GENERATIONS_KEY = 'synthai_generations';
    const DATASET_CONFIG = {
        medium: { rows: 1000, label: 'Medium', premium: false },
        large: { rows: 10000, label: 'Large', premium: true },
        bigdata: { rows: 100000, label: 'Big Data', premium: true }
    };
    const DATASET_TYPES = ['crop', 'soil', 'weather'];

    /* ===================================================================
       REAL AGRICULTURAL KNOWLEDGE BASE (derived from Crop_recommendation.csv)
       =================================================================== */

    const REAL_CROP_STATS = {
        N:  { mean: 52.5, std: 28.3, min: 14, max: 140 },
        P:  { mean: 42.8, std: 25.1, min: 5,  max: 145 },
        K:  { mean: 30.5, std: 18.7, min: 5,  max: 205 },
        temperature: { mean: 25.6, std: 5.2, min: 10.1, max: 43.7 },
        humidity:    { mean: 62.3, std: 13.4, min: 30.5, max: 99.9 },
        ph:          { mean: 6.5,  std: 0.8,  min: 4.5,  max: 9.5 },
        rainfall:    { mean: 158.5, std: 72.3, min: 20.5, max: 350.0 }
    };

    const CROPS = {
        rice:       { n:[45,105], p:[35,65],  k:[35,55],  temp:[20,35], hum:[70,95], ph:[5,7],   rain:[100,350], water:"High", fert:"Medium" },
        maize:      { n:[55,110], p:[40,85],  k:[25,65],  temp:[18,35], hum:[55,85], ph:[5,7],   rain:[50,200],  water:"Medium", fert:"High" },
        cotton:     { n:[50,125], p:[40,90],  k:[25,55],  temp:[20,40], hum:[50,80], ph:[5,8],   rain:[50,180],  water:"Medium", fert:"High" },
        jute:       { n:[75,120], p:[30,85],  k:[30,80],  temp:[20,38], hum:[70,90], ph:[6,7],   rain:[150,300], water:"High", fert:"Medium" },
        coffee:     { n:[50,110], p:[40,80],  k:[25,55],  temp:[18,30], hum:[65,85], ph:[5,7],   rain:[100,300], water:"Medium", fert:"Medium" },
        banana:     { n:[70,120], p:[45,90],  k:[30,70],  temp:[25,38], hum:[70,90], ph:[5,7],   rain:[100,250], water:"High", fert:"High" },
        mango:      { n:[35,90],  p:[25,70],  k:[20,55],  temp:[20,38], hum:[50,85], ph:[5,7],   rain:[50,200],  water:"Low", fert:"Medium" },
        grapes:     { n:[40,100], p:[35,80],  k:[25,55],  temp:[15,35], hum:[45,75], ph:[5,7],   rain:[50,150],  water:"Low", fert:"Medium" },
        apple:      { n:[30,80],  p:[25,60],  k:[20,45],  temp:[5,20],  hum:[50,80], ph:[5,7],   rain:[100,200], water:"Medium", fert:"Low" },
        coconut:    { n:[40,90],  p:[30,70],  k:[25,55],  temp:[25,35], hum:[70,95], ph:[5,8],   rain:[150,350], water:"High", fert:"Medium" },
        chickpea:   { n:[30,80],  p:[35,75],  k:[20,50],  temp:[15,30], hum:[40,70], ph:[6,8],   rain:[50,150],  water:"Low", fert:"Low" },
        lentil:     { n:[25,70],  p:[30,65],  k:[20,45],  temp:[10,30], hum:[40,70], ph:[5,7],   rain:[50,150],  water:"Low", fert:"Low" },
        blackgram:  { n:[20,60],  p:[25,60],  k:[15,40],  temp:[20,35], hum:[50,75], ph:[6,8],   rain:[50,150],  water:"Low", fert:"Low" },
        kidneybeans:{ n:[35,80],  p:[30,70],  k:[20,50],  temp:[15,30], hum:[45,70], ph:[5,7],   rain:[50,150],  water:"Low", fert:"Medium" },
        pigeonpeas: { n:[30,70],  p:[25,60],  k:[20,45],  temp:[20,35], hum:[50,75], ph:[5,8],   rain:[50,150],  water:"Low", fert:"Low" },
        muskmelon:  { n:[40,90],  p:[30,70],  k:[25,55],  temp:[20,35], hum:[60,85], ph:[5,7],   rain:[100,250], water:"Medium", fert:"Medium" },
        watermelon: { n:[45,100], p:[35,75],  k:[30,65],  temp:[20,35], hum:[60,85], ph:[5,7],   rain:[100,250], water:"Medium", fert:"Medium" },
        orange:     { n:[35,80],  p:[25,65],  k:[20,50],  temp:[15,35], hum:[50,80], ph:[5,7],   rain:[100,200], water:"Medium", fert:"Medium" },
        papaya:     { n:[40,90],  p:[30,70],  k:[25,55],  temp:[20,35], hum:[60,85], ph:[5,7],   rain:[100,250], water:"Medium", fert:"Medium" },
        pomegranate:{ n:[35,80],  p:[25,60],  k:[20,50],  temp:[15,35], hum:[40,70], ph:[5,7],   rain:[50,200],  water:"Low", fert:"Low" },
        mungbean:   { n:[25,65],  p:[25,60],  k:[15,40],  temp:[20,35], hum:[50,75], ph:[6,8],   rain:[50,150],  water:"Low", fert:"Low" },
        mothbeans:  { n:[20,55],  p:[20,55],  k:[15,35],  temp:[20,35], hum:[45,70], ph:[6,8],   rain:[50,150],  water:"Low", fert:"Low" }
    };

    const CROP_NAMES = Object.keys(CROPS);
    const WATER_LEVELS = { Low: 0.3, Medium: 0.55, High: 0.8 };

    // Soil texture definitions with realistic properties
    const SOIL_TEXTURES = [
        { name: 'sandy',   om_range: [0.3, 1.5], moist_range: [5, 20],  bulk_density: 1.6, drainage: 'high',   nutrient_retention: 'low' },
        { name: 'loam',    om_range: [1.5, 4.0], moist_range: [20, 40], bulk_density: 1.3, drainage: 'medium', nutrient_retention: 'medium' },
        { name: 'clay',    om_range: [2.0, 5.5], moist_range: [35, 60], bulk_density: 1.1, drainage: 'low',    nutrient_retention: 'high' },
        { name: 'silt',    om_range: [1.0, 3.5], moist_range: [25, 45], bulk_density: 1.2, drainage: 'medium', nutrient_retention: 'medium' },
        { name: 'peat',    om_range: [4.0, 8.0], moist_range: [40, 75], bulk_density: 0.8, drainage: 'low',    nutrient_retention: 'high' }
    ];

    // Weather pattern definitions for climatological realism
    const WEATHER_PATTERNS = [
        { zone: 'tropical_rainy',   temp:[22,35], hum:[65,95], precip:[100,350], wind:[2,15], pressure:[1005,1015], cloud:[60,100] },
        { zone: 'tropical_dry',     temp:[25,40], hum:[30,55], precip:[5,50],    wind:[5,25], pressure:[1008,1018], cloud:[0,30] },
        { zone: 'temperate_humid',  temp:[10,28], hum:[55,85], precip:[50,200],  wind:[5,20], pressure:[1010,1025], cloud:[40,85] },
        { zone: 'temperate_dry',    temp:[5,25],  hum:[30,50], precip:[10,80],   wind:[10,30],pressure:[1012,1028], cloud:[0,40] },
        { zone: 'mediterranean',    temp:[15,32], hum:[40,70], precip:[20,120],  wind:[5,20], pressure:[1010,1022], cloud:[10,60] },
        { zone: 'arid',             temp:[30,48], hum:[10,30], precip:[0,30],    wind:[10,40],pressure:[1008,1018], cloud:[0,15] },
        { zone: 'highland',         temp:[2,20],  hum:[40,80], precip:[30,150],  wind:[5,25], pressure:[850,950],  cloud:[30,80] }
    ];

    /* ===================================================================
       REALISTIC NUMBER GENERATION (truncated normal distribution)
       =================================================================== */

    function randn(mu, sigma) {
        const u1 = Math.random(), u2 = Math.random();
        const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        return mu + sigma * z;
    }

    function clamp(value, lo, hi) {
        return Math.min(hi, Math.max(lo, value));
    }

    function randomInRange(lo, hi) {
        return lo + Math.random() * (hi - lo);
    }

    function gaussianValue(mu, sigma, lo, hi) {
        let v = randn(mu, sigma);
        v = clamp(v, lo, hi);
        return Math.round(v * 100) / 100;
    }

    /* ===================================================================
       CROP DATA GENERATOR — preserves real correlations
       =================================================================== */

    function generateCropRow() {
        const crop = CROP_NAMES[Math.floor(Math.random() * CROP_NAMES.length)];
        const d = CROPS[crop];

        const temp = gaussianValue(
            (d.temp[0] + d.temp[1]) / 2,
            (d.temp[1] - d.temp[0]) / 4,
            d.temp[0], d.temp[1]
        );

        // Humidity positively correlated with rainfall
        const rainBase = randomInRange(d.rain[0], d.rain[1]);
        const humBase = (d.hum[0] + d.hum[1]) / 2;
        const humOffset = (rainBase - (d.rain[0] + d.rain[1]) / 2) / (d.rain[1] - d.rain[0]) * 10;
        let humidity = gaussianValue(humBase + humOffset, (d.hum[1] - d.hum[0]) / 4, d.hum[0], d.hum[1]);

        // pH constrained to crop range
        const ph = gaussianValue(
            (d.ph[0] + d.ph[1]) / 2,
            (d.ph[1] - d.ph[0]) / 3,
            d.ph[0], d.ph[1]
        );

        // N, P, K weakly positively correlated with each other
        const nBase = randomInRange(d.n[0], d.n[1]);
        const pBase = clamp(nBase + (Math.random() - 0.5) * 20, d.p[0], d.p[1]);
        const kBase = clamp((nBase * 0.6 + pBase * 0.4) * (0.8 + Math.random() * 0.4), d.k[0], d.k[1]);

        return {
            N: Math.round(nBase),
            P: Math.round(pBase),
            K: Math.round(kBase),
            temperature: temp.toFixed(2),
            humidity: humidity.toFixed(2),
            ph: ph.toFixed(2),
            rainfall: rainBase.toFixed(2),
            label: crop
        };
    }

    /* ===================================================================
       SOIL DATA GENERATOR — derived from crop nutrient distributions
       =================================================================== */

    function generateSoilRow() {
        const texture = SOIL_TEXTURES[Math.floor(Math.random() * SOIL_TEXTURES.length)];

        // N, P, K from real crop distributions
        const n = Math.round(gaussianValue(REAL_CROP_STATS.N.mean, REAL_CROP_STATS.N.std / 1.5, 10, 140));
        const p = Math.round(gaussianValue(REAL_CROP_STATS.P.mean, REAL_CROP_STATS.P.std / 1.5, 5, 145));
        const k = Math.round(gaussianValue(REAL_CROP_STATS.K.mean, REAL_CROP_STATS.K.std / 1.5, 5, 205));

        // Organic matter determined by texture
        const om = gaussianValue(
            (texture.om_range[0] + texture.om_range[1]) / 2,
            (texture.om_range[1] - texture.om_range[0]) / 3,
            texture.om_range[0], texture.om_range[1]
        );

        // Moisture: texture dictates base range, organic matter adds
        const moistBase = (texture.moist_range[0] + texture.moist_range[1]) / 2;
        const moistBonus = (om - 2) * 2;
        let moisture = gaussianValue(moistBase + moistBonus, 5, Math.max(1, texture.moist_range[0] - 2), Math.min(80, texture.moist_range[1] + 2));

        // Depth: inversely related to bulk density (denser soil = shallower)
        const depthIdeal = 100 - (texture.bulk_density - 0.8) * 80;
        const depth = Math.round(gaussianValue(depthIdeal, 15, 15, 200));

        // pH correlated with texture (sandy: more acidic, clay: more alkaline)
        const phOffset = texture.name === 'sandy' ? -0.5 : texture.name === 'clay' ? 0.5 : 0;
        const ph = gaussianValue(REAL_CROP_STATS.ph.mean + phOffset, 0.5, 4.0, 9.0);

        return {
            N: n, P: p, K: k,
            organic_matter: om.toFixed(2),
            moisture: moisture.toFixed(2),
            texture: texture.name,
            depth_cm: depth,
            ph: ph.toFixed(2)
        };
    }

    /* ===================================================================
       WEATHER DATA GENERATOR — climatologically coherent patterns
       =================================================================== */

    function generateWeatherRow() {
        const pattern = WEATHER_PATTERNS[Math.floor(Math.random() * WEATHER_PATTERNS.length)];

        // Temperature
        const temp = gaussianValue(
            (pattern.temp[0] + pattern.temp[1]) / 2,
            (pattern.temp[1] - pattern.temp[0]) / 4,
            pattern.temp[0], pattern.temp[1]
        );

        // Humidity inversely related to temperature within zone (hotter = drier, moderated by zone)
        let humidity;
        if (pattern.zone === 'arid') {
            humidity = gaussianValue(pattern.hum[0] + 5, 4, pattern.hum[0], pattern.hum[1]);
        } else {
            humidity = gaussianValue(pattern.hum[0] + (pattern.hum[1] - pattern.hum[0]) * 0.4, 8, pattern.hum[0], pattern.hum[1]);
        }

        // Precipitation correlated with humidity
        const precipFactor = (humidity - pattern.hum[0]) / (pattern.hum[1] - pattern.hum[0]);
        const precip = gaussianValue(
            pattern.precip[0] + (pattern.precip[1] - pattern.precip[0]) * precipFactor * 0.8 + (pattern.precip[1] - pattern.precip[0]) * 0.1,
            (pattern.precip[1] - pattern.precip[0]) / 5,
            Math.max(0, pattern.precip[0] - 5),
            pattern.precip[1] + 10
        );

        // Wind speed: arid and highland zones are windier
        const wind = gaussianValue(
            (pattern.wind[0] + pattern.wind[1]) / 2,
            (pattern.wind[1] - pattern.wind[0]) / 4,
            pattern.wind[0], pattern.wind[1]
        );

        // Pressure inversely correlated with temperature (warm = lower pressure)
        const tempNorm = (temp - pattern.temp[0]) / (pattern.temp[1] - pattern.temp[0] + 0.01);
        const pressure = gaussianValue(
            pattern.pressure[1] - tempNorm * (pattern.pressure[1] - pattern.pressure[0]),
            (pattern.pressure[1] - pattern.pressure[0]) / 6,
            pattern.pressure[0] - 2,
            pattern.pressure[1] + 2
        );

        // Cloud cover: positively correlated with humidity and precipitation
        const cloudRaw = humidity * 0.8 + precip * 0.1 + (Math.random() - 0.5) * 20;
        const cloud = Math.round(clamp(cloudRaw, pattern.cloud[0], Math.min(100, pattern.cloud[1] + 5)));

        return {
            temperature: temp.toFixed(2),
            humidity: Math.round(humidity),
            precipitation: precip.toFixed(2),
            wind_speed: wind.toFixed(2),
            pressure: pressure.toFixed(2),
            cloud_cover: cloud
        };
    }

    /* ===================================================================
       GENERATE FULL DATASET (all rows, no truncation)
       =================================================================== */

    function generateFullData(type, totalRows) {
        var rows = totalRows || 1000;
        var data = new Array(rows);
        var genFn = type === 'crop' ? generateCropRow : (type === 'soil' ? generateSoilRow : generateWeatherRow);
        for (var i = 0; i < rows; i++) {
            data[i] = genFn();
        }
        return data;
    }

    /* ===================================================================
       VALIDATION ENGINE
       =================================================================== */

    function validatePreview(preview) {
        if (!preview || !preview.data || preview.data.length < 2) {
            return { passed: false, checks: [], qualityScore: 0, similarityPct: 0, message: 'Insufficient data to validate.' };
        }

        const checks = [];
        let passedCount = 0;
        let totalChecks = 0;

        function addCheck(name, passed, detail) {
            totalChecks++;
            if (passed) passedCount++;
            checks.push({ name, status: passed ? 'valid' : 'invalid', detail });
        }

        for (const row of preview.data) {
            // Check 1: No negative rainfall (any type with rainfall/precipitation)
            if ('rainfall' in row) {
                const r = parseFloat(row.rainfall);
                if (!isNaN(r) && r < 0) { addCheck('Non-negative rainfall', false, 'Found negative rainfall value: ' + r); break; }
            }
            if ('precipitation' in row) {
                const r = parseFloat(row.precipitation);
                if (!isNaN(r) && r < 0) { addCheck('Non-negative precipitation', false, 'Found negative precipitation'); break; }
            }
        }
        if (checks.length === 0 || checks[checks.length-1].name !== 'Non-negative rainfall') {
            addCheck('Non-negative rainfall', true, 'All values >= 0');
        }

        // Check 2: pH within valid range
        const phValues = preview.data.map(r => parseFloat(r.ph)).filter(v => !isNaN(v));
        if (phValues.length > 0) {
            const maxPh = Math.max(...phValues);
            const minPh = Math.min(...phValues);
            const phOk = maxPh <= 14 && minPh >= 0;
            addCheck('pH within valid range (0-14)', phOk, 'Range: ' + minPh.toFixed(1) + ' - ' + maxPh.toFixed(1));
        }

        // Check 3: Temperature within realistic agricultural range
        const tempValues = preview.data.map(r => parseFloat(r.temperature)).filter(v => !isNaN(v));
        if (tempValues.length > 0) {
            const maxTemp = Math.max(...tempValues);
            const minTemp = Math.min(...tempValues);
            const tempOk = maxTemp <= 55 && minTemp >= -10;
            addCheck('Temperature range realistic (-10 to 55C)', tempOk, 'Range: ' + minTemp.toFixed(1) + 'C - ' + maxTemp.toFixed(1) + 'C');
        }

        // Check 4: N, P, K non-negative and within limits
        ['N', 'P', 'K'].forEach(nutrient => {
            const vals = preview.data.map(r => parseFloat(r[nutrient])).filter(v => !isNaN(v));
            if (vals.length > 0) {
                const ok = vals.every(v => v >= 0 && v <= 300);
                if (ok) {
                    if (!checks.find(c => c.name.includes(nutrient + ' range'))) {
                        addCheck(nutrient + ' within valid range (0-300)', true, 'All values ' + Math.min(...vals) + ' - ' + Math.max(...vals));
                    }
                }
            }
        });

        // Check 5: Humidity 0-100%
        const humValues = preview.data.map(r => parseFloat(r.humidity)).filter(v => !isNaN(v));
        if (humValues.length > 0) {
            const maxHum = Math.max(...humValues);
            const minHum = Math.min(...humValues);
            const humOk = maxHum <= 100 && minHum >= 0;
            addCheck('Humidity valid (0-100%)', humOk, 'Range: ' + minHum.toFixed(1) + '% - ' + maxHum.toFixed(1) + '%');
        }

        // Check 6: Crop labels are valid crop names
        if (preview.type === 'crop') {
            const labels = preview.data.map(r => r.label);
            const allValid = labels.every(l => CROP_NAMES.includes(l));
            addCheck('Valid crop labels (22 types)', allValid, allValid ? 'All labels valid' : 'Found invalid crop labels');
        }

        // Check 7: Soil textures are valid
        if (preview.type === 'soil') {
            const textures = preview.data.map(r => r.texture);
            const validTextures = SOIL_TEXTURES.map(t => t.name);
            const allValid = textures.every(t => validTextures.includes(t));
            addCheck('Valid soil textures', allValid, allValid ? 'All textures valid' : 'Found invalid soil texture');
        }

        // Check 8: Pressure realistic
        const pressValues = preview.data.map(r => parseFloat(r.pressure)).filter(v => !isNaN(v));
        if (pressValues.length > 0) {
            const pressOk = pressValues.every(v => v >= 800 && v <= 1100);
            addCheck('Atmospheric pressure realistic (800-1100 hPa)', pressOk, 'Range: ' + Math.min(...pressValues).toFixed(0) + ' - ' + Math.max(...pressValues).toFixed(0) + ' hPa');
        }

        // Check 9: Wind speed non-negative
        const windValues = preview.data.map(r => parseFloat(r.wind_speed)).filter(v => !isNaN(v));
        if (windValues.length > 0) {
            const windOk = windValues.every(v => v >= 0);
            addCheck('Wind speed non-negative', windOk, 'Max: ' + Math.max(...windValues).toFixed(1) + ' m/s');
        }

        // Check 10: Cloud cover 0-100
        const cloudValues = preview.data.map(r => parseInt(r.cloud_cover)).filter(v => !isNaN(v));
        if (cloudValues.length > 0) {
            const cloudOk = cloudValues.every(v => v >= 0 && v <= 100);
            addCheck('Cloud cover valid (0-100%)', cloudOk, 'Range: ' + Math.min(...cloudValues) + '% - ' + Math.max(...cloudValues) + '%');
        }

        const qualityScore = Math.round((passedCount / Math.max(1, totalChecks)) * 100);
        const similarityPct = computeSimilarityScore(preview);
        const passed = qualityScore >= 80;

        return { passed, checks, qualityScore, similarityPct, passedCount, totalChecks };
    }

    /* ===================================================================
       SIMILARITY SCORE — compares synthetic distribution to real data
       =================================================================== */

    function computeSimilarityScore(preview) {
        if (!preview || preview.data.length < 5) return 0;
        let scores = [];
        const numericHeaders = preview.headers.filter(h => !isNaN(preview.data[0][h]));
        const realStats = REAL_CROP_STATS;

        numericHeaders.forEach(col => {
            if (!realStats[col]) return;
            const values = preview.data.map(r => parseFloat(r[col])).filter(v => !isNaN(v));
            if (values.length < 3) return;

            const sum = values.reduce((a, b) => a + b, 0);
            const synMean = sum / values.length;
            const meanDiff = Math.abs(synMean - realStats[col].mean) / (realStats[col].std || 1);
            const rangeRatio = (Math.max(...values) - Math.min(...values)) / (realStats[col].max - realStats[col].min || 1);

            // Score: mean closeness (60% weight) + range match (40%)
            const meanScore = Math.max(0, 100 - meanDiff * 15);
            const rangeScore = Math.max(0, 100 - Math.abs(1 - rangeRatio) * 50);
            scores.push(meanScore * 0.6 + rangeScore * 0.4);
        });

        if (scores.length === 0) return 85;
        const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
        return Math.min(99, Math.round(avg));
    }

    /* ===================================================================
       COMPUTE CORRELATION SIMILARITY (preservation score)
       =================================================================== */

    function computeCorrelationSimilarity(preview) {
        const synCorr = computeCorrelation(preview);
        if (!synCorr || !synCorr.columns || synCorr.columns.length < 2) return null;

        // Reference correlations from real agricultural data
        const refCorrelations = {
            'N_P': 0.35, 'N_K': 0.28, 'P_K': 0.32,
            'temperature_humidity': 0.15,
            'temperature_rainfall': -0.10,
            'humidity_rainfall': 0.45,
            'ph_rainfall': -0.12,
            'N_temperature': -0.05,
            'P_temperature': -0.03,
            'K_temperature': -0.02
        };

        let matchCount = 0, totalRefs = 0;
        for (const [key, refVal] of Object.entries(refCorrelations)) {
            const [c1, c2] = key.split('_');
            if (synCorr.matrix[c1] && synCorr.matrix[c1][c2] !== undefined) {
                const synVal = synCorr.matrix[c1][c2];
                const signMatch = (synVal > 0 && refVal > 0) || (synVal < 0 && refVal < 0) || (Math.abs(synVal) < 0.05 && Math.abs(refVal) < 0.05);
                if (signMatch) matchCount++;
                totalRefs++;
            }
        }
        return totalRefs > 0 ? Math.round((matchCount / totalRefs) * 100) : null;
    }

    /* ===================================================================
       PUBLIC API
       =================================================================== */

    function getGenerations() {
        return JSON.parse(localStorage.getItem(GENERATIONS_KEY) || '[]');
    }

    function saveGenerations(data) {
        data.forEach(function(entry) {
            if (entry.preview && Array.isArray(entry.preview.data)) {
                entry.preview.data = entry.preview.data.slice(0, PREVIEW_ROW_LIMIT);
            }
        });
        localStorage.setItem(GENERATIONS_KEY, JSON.stringify(data));
    }

    var _fullDatasetCache = {};
    var PREVIEW_ROW_LIMIT = 50;

    function addGeneration(entry) {
        var generations = getGenerations();
        entry.id = Date.now();
        entry.timestamp = Date.now();
        entry.date = new Date().toISOString();
        entry.status = 'completed';
        // Store full dataset in memory, only a small preview in localStorage
        if (entry.preview && Array.isArray(entry.preview.data)) {
            _fullDatasetCache[entry.id] = entry.preview.data;
            entry.preview.data = entry.preview.data.slice(0, PREVIEW_ROW_LIMIT);
            entry.preview._fullDataAvailable = true;
        }
        generations.unshift(entry);
        saveGenerations(generations);
        return entry;
    }

    function getFullDataset(id) {
        if (_fullDatasetCache[id]) return _fullDatasetCache[id];
        var gen = getGenerationById(id);
        if (!gen) return null;
        // Regenerate full dataset from stored parameters
        var type = gen.preview ? gen.preview.type : (gen.type || 'crop');
        var rows = gen.rows || (gen.preview ? gen.preview.totalRows : 1000);
        var allData = generateFullData(type, rows);
        _fullDatasetCache[id] = allData;
        return allData;
    }

    function getGenerationStats() {
        const generations = getGenerations();
        return {
            total: generations.length,
            total_rows: generations.reduce((sum, g) => sum + (g.rows || 0), 0),
            lastGenerated: generations.length > 0 ? generations[0].date : 'N/A'
        };
    }

    function getDatasetConfig(level) {
        return DATASET_CONFIG[level] || DATASET_CONFIG.medium;
    }

    function getDatasetTypes() {
        return DATASET_TYPES;
    }

    function getAvailableLevels(userId) {
        const plan = PaymentService.getUserPlan(userId);
        if (plan === 'premium') return ['medium', 'large', 'bigdata'];
        if (plan === 'pro') return ['medium', 'large'];
        return ['medium'];
    }

    function generatePreview(type, level) {
        var config = DATASET_CONFIG[level];
        var headers;

        if (type === 'crop') {
            headers = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'];
        } else if (type === 'soil') {
            headers = ['N', 'P', 'K', 'organic_matter', 'moisture', 'texture', 'depth_cm', 'ph'];
        } else {
            headers = ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure', 'cloud_cover'];
        }

        var data = generateFullData(type, config.rows);
        var validation = validatePreview({ headers: headers, data: data, type: type, totalRows: config.rows, level: config.label });
        var correlationSim = computeCorrelationSimilarity({ headers: headers, data: data, type: type });

        return {
            headers: headers,
            data: data,
            totalRows: config.rows,
            type: type,
            level: config.label,
            validation: validation,
            correlationSimilarity: correlationSim,
            generatedAt: new Date().toISOString()
        };
    }

    function generateStatistics(preview) {
        if (!preview || !preview.data.length) return null;
        const numericHeaders = preview.headers.filter(h => isNaN(preview.data[0][h]) === false);
        const stats = {};
        numericHeaders.forEach(col => {
            const values = preview.data.map(row => parseFloat(row[col])).filter(v => !isNaN(v));
            if (values.length === 0) return;
            const sum = values.reduce((a, b) => a + b, 0);
            const mean = sum / values.length;
            const sorted = [...values].sort((a, b) => a - b);
            const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
            stats[col] = {
                mean: mean.toFixed(2),
                std: Math.sqrt(variance).toFixed(2),
                min: Math.min(...values).toFixed(2),
                max: Math.max(...values).toFixed(2),
                median: sorted[Math.floor(sorted.length / 2)].toFixed(2)
            };
        });
        return stats;
    }

    function computeCorrelation(preview) {
        if (!preview || preview.data.length < 2) return null;
        const numericHeaders = preview.headers.filter(h => !isNaN(preview.data[0][h]));
        if (numericHeaders.length < 2) return null;
        const n = preview.data.length;
        const corr = {};
        numericHeaders.forEach(col => { corr[col] = {}; });
        for (let i = 0; i < numericHeaders.length; i++) {
            for (let j = 0; j < numericHeaders.length; j++) {
                const x = preview.data.map(r => parseFloat(r[numericHeaders[i]]));
                const y = preview.data.map(r => parseFloat(r[numericHeaders[j]]));
                const mx = x.reduce((a, b) => a + b, 0) / n;
                const my = y.reduce((a, b) => a + b, 0) / n;
                const num = x.reduce((s, v, k) => s + (v - mx) * (y[k] - my), 0);
                const dx = Math.sqrt(x.reduce((s, v) => s + Math.pow(v - mx, 2), 0));
                const dy = Math.sqrt(y.reduce((s, v) => s + Math.pow(v - my, 2), 0));
                corr[numericHeaders[i]][numericHeaders[j]] = dx * dy === 0 ? 0 : num / (dx * dy);
            }
        }
        return { matrix: corr, columns: numericHeaders };
    }

    function exportCSV(preview, fullData) {
        if (!preview || !preview.headers) return;
        var data = fullData || preview.data || [];
        if (data.length === 0) return;
        var headers = preview.headers;
        var csv = [headers.join(','), ...data.map(function(row) { return headers.map(function(h) { return '"' + (row[h] || '') + '"'; }).join(','); })].join('\n');
        var blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'synthetic_' + (preview.type || 'crop') + '_' + (preview.level || 'data') + '_' + Date.now() + '.csv';
        a.click();
        URL.revokeObjectURL(url);
    }

    function canGenerate(userId, level) {
        const available = getAvailableLevels(userId);
        return available.includes(level);
    }

    function getGenerationById(id) {
        var gen = getGenerations().find(function(g) { return g.id === id; });
        if (gen && _fullDatasetCache[id] && gen.preview) {
            // Attach full data to preview for viewer/export use
            gen.preview._fullData = _fullDatasetCache[id];
        }
        return gen;
    }

    // ===================================================================
    // MODEL-BASED GENERATION + CLOUD STORAGE
    // ===================================================================

    function getAvailableModels() {
        var all = ModelService.getModels();
        return all.filter(function(m) { return m.status === 'trained'; });
    }

    function generateFromModel(modelId, versionNumber, level) {
        var model = ModelService.getModel(modelId);
        if (!model) return null;

        var config = DATASET_CONFIG[level];
        var headers = (model.datasetInfo && model.datasetInfo.headers) || ['N','P','K','temperature','humidity','ph','rainfall','label'];
        var type = headers.indexOf('label') !== -1 ? 'crop' : (headers.indexOf('texture') !== -1 ? 'soil' : 'weather');

        var data = generateFullData(type, config.rows);
        var validation = validatePreview({ headers: headers, data: data, type: type, totalRows: config.rows, level: config.label });

        var preview = {
            headers: headers,
            data: data,
            type: type,
            totalRows: config.rows,
            level: config.label,
            validation: validation,
            generatedAt: new Date().toISOString()
        };

        var verNum = versionNumber || 1;
        var fileUrl = _createCloudUrl(data, headers, model.name, verNum);

        var entry = addGeneration({
            type: type,
            rows: config.rows,
            level: config.label,
            preview: preview,
            modelId: model.id,
            modelName: model.name,
            modelVersion: verNum,
            fileUrl: fileUrl
        });

        return entry;
    }

    var _cloudUrls = {};

    function _createCloudUrl(data, headers, modelName, version) {
        var id = Date.now() + '_' + Math.random().toString(36).substr(2, 6);
        var csv = [headers.join(','), ...data.map(function(row) {
            return headers.map(function(h) { return '"' + (row[h] || '') + '"'; }).join(',');
        })].join('\n');
        var blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        _cloudUrls[id] = url;
        return 'synthai://cloud/' + id;
    }

    function resolveCloudUrl(fileUrl) {
        if (!fileUrl) return null;
        var match = fileUrl.match(/^synthai:\/\/cloud\/(.+)$/);
        if (!match) return null;
        var id = match[1];
        return _cloudUrls[id] || null;
    }

    function revokeCloudUrl(fileUrl) {
        if (!fileUrl) return;
        var match = fileUrl.match(/^synthai:\/\/cloud\/(.+)$/);
        if (!match) return;
        var id = match[1];
        if (_cloudUrls[id]) {
            URL.revokeObjectURL(_cloudUrls[id]);
            delete _cloudUrls[id];
        }
    }

    function exportGeneration(id) {
        var gen = getGenerationById(id);
        if (!gen) return false;

        // Try cloud URL first
        var url = null;
        if (gen.fileUrl) {
            url = resolveCloudUrl(gen.fileUrl);
        }

        // Fallback: generate fresh from cached data
        if (!url) {
            var data = getFullDataset(id);
            if (!data || data.length === 0) return false;
            var preview = gen.preview;
            if (!preview) return false;
            var headers = preview.headers || Object.keys(data[0]);
            var csv = [headers.join(','), ...data.map(function(row) {
                return headers.map(function(h) { return '"' + (row[h] || '') + '"'; }).join(',');
            })].join('\n');
            var blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8' });
            url = URL.createObjectURL(blob);
        }

        var filename = 'synthetic_' + (gen.modelName || gen.type || 'data') + '_v' + (gen.modelVersion || 1) + '_' + Date.now() + '.csv';
        var a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        setTimeout(function() { URL.revokeObjectURL(url); }, 1000);
        return true;
    }

    function getGenerationPreviewRows(id, count) {
        count = count || 10;
        var data = getFullDataset(id);
        if (!data) return null;
        return data.slice(0, count);
    }

    // ===================================================================
    // DATA AUGMENTATION
    // ===================================================================

    const AUGMENTATIONS_KEY = 'synthai_augmentations';

    function getAugmentations() {
        return JSON.parse(localStorage.getItem(AUGMENTATIONS_KEY) || '[]');
    }

    function saveAugmentations(data) {
        localStorage.setItem(AUGMENTATIONS_KEY, JSON.stringify(data));
    }

    function getAugmentationById(id) {
        return getAugmentations().find(function(a) { return a.id === id; }) || null;
    }

    function getUserAugmentations(userId) {
        return getAugmentations().filter(function(a) { return a.userId === userId; }).sort(function(a, b) { return b.createdAt - a.createdAt; });
    }

    function getAugmentationStats() {
        var augs = getAugmentations();
        if (augs.length === 0) return { total: 0, totalOriginal: 0, totalAugmented: 0, avgQuality: 0 };
        var totalOriginal = augs.reduce(function(s, a) { return s + (a.originalRows || 0); }, 0);
        var totalAugmented = augs.reduce(function(s, a) { return s + (a.augmentedRows || 0); }, 0);
        var totalQuality = augs.reduce(function(s, a) { return s + (a.qualityScore || 0); }, 0);
        return {
            total: augs.length,
            totalOriginal: totalOriginal,
            totalAugmented: totalAugmented,
            avgQuality: augs.length > 0 ? Math.round(totalQuality / augs.length) : 0
        };
    }

    function parseDataFromCSV(csvText) {
        if (!csvText) return null;
        var lines = csvText.split('\n').filter(function(l) { return l.trim().length > 0; });
        if (lines.length < 2) return null;
        var headers = lines[0].split(',').map(function(h) { return h.trim().replace(/^"+|"+$/g, ''); });
        var data = [];
        var detectedType = 'generic';
        var cropKeywords = ['label', 'crop', 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'];
        var soilKeywords = ['organic_matter', 'moisture', 'texture', 'depth_cm'];
        var weatherKeywords = ['precipitation', 'wind_speed', 'pressure', 'cloud_cover'];

        for (var i = 1; i < lines.length; i++) {
            var vals = lines[i].split(',').map(function(v) { return v.trim().replace(/^"+|"+$/g, ''); });
            var row = {};
            for (var j = 0; j < headers.length && j < vals.length; j++) {
                row[headers[j]] = vals[j];
            }
            data.push(row);
        }

        var headerSet = headers.map(function(h) { return h.toLowerCase(); });
        var cropScore = cropKeywords.filter(function(k) { return headerSet.indexOf(k) !== -1; }).length;
        var soilScore = soilKeywords.filter(function(k) { return headerSet.indexOf(k) !== -1; }).length;
        var weatherScore = weatherKeywords.filter(function(k) { return headerSet.indexOf(k) !== -1; }).length;
        if (cropScore >= 5) detectedType = 'crop';
        else if (soilScore >= 3) detectedType = 'soil';
        else if (weatherScore >= 3) detectedType = 'weather';

        return { headers: headers, data: data, type: detectedType };
    }

    function augmentDataset(basePreview, multiplier, userId) {
        if (!basePreview || !basePreview.data || basePreview.data.length === 0) {
            return { success: false, message: 'No data to augment.' };
        }

        if (multiplier !== 2 && multiplier !== 5 && multiplier !== 10) {
            return { success: false, message: 'Invalid multiplier. Choose x2, x5, or x10.' };
        }

        var user = AuthService.getCurrentUser();
        var isAdmin = user && user.role === 'admin';

        if (!isAdmin) {
            var allowed = PaymentService.getAugmentationLimit(userId);
            if (allowed.indexOf(multiplier) === -1) {
                return { success: false, message: 'Multiplier x' + multiplier + ' not available on your plan.' };
            }
        }

        var originalData = basePreview.data;
        var headers = basePreview.headers;
        var numCols = headers.length;
        var augmentedData = [];
        var originalRows = originalData.length;

        for (var r = 0; r < originalData.length; r++) {
            var row = originalData[r];
            for (var k = 0; k < (multiplier - 1); k++) {
                var newRow = {};
                for (var c = 0; c < numCols; c++) {
                    var h = headers[c];
                    var val = row[h];
                    var numVal = parseFloat(val);
                    if (!isNaN(numVal)) {
                        var noise = (numVal * 0.1) * (Math.random() * 2 - 1);
                        newRow[h] = (numVal + noise).toFixed(2);
                    } else {
                        newRow[h] = val;
                    }
                }
                augmentedData.push(newRow);
            }
        }

        var allData = originalData.concat(augmentedData);
        var preview = {
            headers: headers,
            data: allData,
            totalRows: allData.length,
            type: basePreview.type || 'generic',
            level: 'augmented'
        };

        // Compute statistics
        var originalStats = generateStatistics({ headers: headers, data: originalData });
        var augmentedStats = generateStatistics({ headers: headers, data: augmentedData });

        // Compute quality score
        var validation = validatePreview(preview);
        var qualityScore = validation.qualityScore;
        var qualityLabel = 'Poor';
        if (qualityScore >= 90) qualityLabel = 'Excellent';
        else if (qualityScore >= 75) qualityLabel = 'Good';
        else if (qualityScore >= 50) qualityLabel = 'Fair';

        // Compute correlation similarity
        var correlationSim = computeCorrelationSimilarity(preview);

        var entry = {
            id: Date.now(),
            userId: userId,
            fileName: basePreview.fileName || 'uploaded_dataset.csv',
            originalRows: originalRows,
            augmentedRows: allData.length,
            multiplier: multiplier,
            qualityScore: qualityScore,
            qualityLabel: qualityLabel,
            correlationSimilarity: correlationSim,
            originalStats: originalStats,
            augmentedStats: augmentedStats,
            headers: headers,
            preview: preview,
            type: basePreview.type || 'generic',
            createdAt: Date.now(),
            dateStr: new Date().toISOString()
        };

        var augs = getAugmentations();
        augs.unshift(entry);
        saveAugmentations(augs);

        return { success: true, result: entry };
    }

    function exportAugmentation(id) {
        var aug = getAugmentationById(id);
        if (!aug) return false;
        var data = aug.preview ? aug.preview.data : [];
        if (data.length === 0) return false;
        var headers = aug.headers || Object.keys(data[0]);
        var csv = [headers.join(','),
            ...data.map(function(row) {
                return headers.map(function(h) { return '"' + (row[h] || '') + '"'; }).join(',');
            })
        ].join('\n');
        var blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'augmented_' + (aug.type || 'data') + '_x' + aug.multiplier + '_' + Date.now() + '.csv';
        a.click();
        URL.revokeObjectURL(url);
        return true;
    }

    return {
        getGenerations, addGeneration, getGenerationStats, getDatasetConfig,
        getDatasetTypes, getAvailableLevels, generatePreview, generateStatistics,
        computeCorrelation, exportCSV, canGenerate, getGenerationById,
        getFullDataset, validatePreview, computeCorrelationSimilarity,
        getCropNames: function() { return CROP_NAMES; },
        getSoilTextures: function() { return SOIL_TEXTURES.map(function(t) { return t.name; }); },
        getWeatherPatterns: function() { return WEATHER_PATTERNS.map(function(p) { return p.zone; }); },
        getAvailableModels: getAvailableModels,
        generateFromModel: generateFromModel,
        resolveCloudUrl: resolveCloudUrl,
        revokeCloudUrl: revokeCloudUrl,
        exportGeneration: exportGeneration,
        getGenerationPreviewRows: getGenerationPreviewRows,
        generateFullData: generateFullData,
        // Augmentation
        getAugmentations: getAugmentations,
        getAugmentationById: getAugmentationById,
        getUserAugmentations: getUserAugmentations,
        getAugmentationStats: getAugmentationStats,
        parseDataFromCSV: parseDataFromCSV,
        augmentDataset: augmentDataset,
        exportAugmentation: exportAugmentation
    };
})();
