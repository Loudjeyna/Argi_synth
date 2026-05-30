/* SynthAI - Model Management Service */
const ModelService = (function() {
    var MODELS_KEY = 'synthai_models';

    function classifyTrainingQuality(generatorLoss, discriminatorLoss) {
        if (generatorLoss < 0.2 && discriminatorLoss < 0.2) return 'good';
        if (generatorLoss <= 0.5 && discriminatorLoss <= 0.5) return 'acceptable';
        return 'needs_improvement';
    }

    function trainingImbalanceWarning(generatorLoss, discriminatorLoss) {
        return Math.abs(generatorLoss - discriminatorLoss) > 0.5;
    }

    function generateLossValues(epochs) {
        var baseGen = 0.8 / Math.sqrt(Math.max(epochs, 10) / 100);
        var baseDisc = 0.6 / Math.sqrt(Math.max(epochs, 10) / 100);
        var genLoss = Math.max(0.05, Math.min(1.5, baseGen + (Math.random() * 0.2 - 0.1)));
        var discLoss = Math.max(0.05, Math.min(1.5, baseDisc + (Math.random() * 0.2 - 0.1)));
        return {
            generatorLoss: Math.round(genLoss * 10000) / 10000,
            discriminatorLoss: Math.round(discLoss * 10000) / 10000
        };
    }

    function getModels() {
        return JSON.parse(localStorage.getItem(MODELS_KEY) || '[]');
    }

    function saveModels(models) {
        localStorage.setItem(MODELS_KEY, JSON.stringify(models));
    }

    function getModel(id) {
        return getModels().find(function(m) { return m.id === id; }) || null;
    }

    function addModel(modelData) {
        var models = getModels();
        var model = {
            id: Date.now(),
            name: modelData.name,
            createdAt: new Date().toISOString(),
            status: 'in_progress',
            config: {
                epochs: parseInt(modelData.epochs) || 10,
                batchSize: parseInt(modelData.batchSize) || 32,
                learningRate: parseFloat(modelData.learningRate) || 0.0002
            },
            datasetInfo: {
                fileName: modelData.fileName || '',
                originalRows: modelData.originalRows || 0,
                originalCols: modelData.originalCols || 0,
                headers: modelData.headers || []
            },
            cleaningReport: modelData.cleaningReport || null,
            trainedModelPath: null,
            generatedIds: [],
            versions: [{
                version: 1,
                type: 'initial',
                createdAt: new Date().toISOString(),
                status: 'in_progress',
                config: {
                    epochs: parseInt(modelData.epochs) || 10,
                    batchSize: parseInt(modelData.batchSize) || 32,
                    learningRate: parseFloat(modelData.learningRate) || 0.0002
                },
                datasetInfo: {
                    fileName: modelData.fileName || '',
                    originalRows: modelData.originalRows || 0,
                    originalCols: modelData.originalCols || 0,
                    headers: modelData.headers || []
                },
                cleaningReport: modelData.cleaningReport || null,
                evaluation: null
            }]
        };
        models.unshift(model);
        saveModels(models);

        // Store full cleaned dataset separately to keep model list lightweight
        if (modelData.cleanedData && modelData.cleanedData.length > 0) {
            try {
                localStorage.setItem('synthai_model_data_' + model.id, JSON.stringify({
                    headers: modelData.headers,
                    rows: modelData.cleanedData
                }));
            } catch (e) {
                console.warn('Could not store full dataset for model ' + model.id + ': ' + e.message);
            }
        }

        return model;
    }

    function updateModel(id, updates) {
        var models = getModels();
        var idx = models.findIndex(function(m) { return m.id === id; });
        if (idx === -1) return null;
        for (var key in updates) {
            if (updates.hasOwnProperty(key)) {
                models[idx][key] = updates[key];
            }
        }
        saveModels(models);
        return models[idx];
    }

    function deleteModel(id) {
        var models = getModels();
        models = models.filter(function(m) { return m.id !== id; });
        saveModels(models);
        localStorage.removeItem('synthai_model_data_' + id);
    }

    function getModelDataset(id) {
        try {
            var data = JSON.parse(localStorage.getItem('synthai_model_data_' + id));
            return data || null;
        } catch (e) {
            return null;
        }
    }

    function getStats() {
        var models = getModels();
        var trained = models.filter(function(m) { return m.status === 'trained'; });
        var failed = models.filter(function(m) { return m.status === 'failed'; });
        var inProgress = models.filter(function(m) { return m.status === 'in_progress'; });
        return {
            total: models.length,
            trained: trained.length,
            failed: failed.length,
            inProgress: inProgress.length
        };
    }

    function searchModels(query, filters) {
        var models = getModels();
        if (query) {
            var q = query.toLowerCase();
            models = models.filter(function(m) { return m.name.toLowerCase().indexOf(q) !== -1; });
        }
        if (filters) {
            if (filters.status && filters.status !== 'all') {
                models = models.filter(function(m) { return m.status === filters.status; });
            }
            if (filters.dateFrom) {
                var from = new Date(filters.dateFrom).getTime();
                models = models.filter(function(m) { return new Date(m.createdAt).getTime() >= from; });
            }
            if (filters.dateTo) {
                var to = new Date(filters.dateTo).getTime() + 86400000;
                models = models.filter(function(m) { return new Date(m.createdAt).getTime() <= to; });
            }
        }
        return models;
    }

    function addGeneratedDataset(modelId, genId) {
        var models = getModels();
        var idx = models.findIndex(function(m) { return m.id === modelId; });
        if (idx === -1) return;
        if (!models[idx].generatedIds) models[idx].generatedIds = [];
        models[idx].generatedIds.push(genId);
        saveModels(models);
    }

    function addVersion(modelId, versionData) {
        var models = getModels();
        var idx = models.findIndex(function(m) { return m.id === modelId; });
        if (idx === -1) return null;
        var model = models[idx];
        if (!model.versions) model.versions = [];
        var nextVer = model.versions.length + 1;
        var version = {
            version: nextVer,
            type: 'retrain',
            createdAt: new Date().toISOString(),
            status: 'in_progress',
            config: {
                epochs: parseInt(versionData.epochs) || 10,
                batchSize: parseInt(versionData.batchSize) || 128,
                learningRate: parseFloat(versionData.learningRate) || 0.0002
            },
            datasetInfo: versionData.datasetInfo || model.datasetInfo || {},
            cleaningReport: versionData.cleaningReport || null,
            evaluation: versionData.evaluation || null
        };
        model.versions.push(version);

        // Update model-level config and datasetInfo to latest
        model.config = version.config;
        model.status = 'in_progress';
        if (versionData.datasetInfo) {
            model.datasetInfo = versionData.datasetInfo;
            model.cleaningReport = versionData.cleaningReport || null;
            // Store new dataset
            if (versionData.cleanedData && versionData.cleanedData.length > 0) {
                try {
                    localStorage.setItem('synthai_model_data_' + modelId, JSON.stringify({
                        headers: versionData.datasetInfo.headers || [],
                        rows: versionData.cleanedData
                    }));
                } catch (e) {
                    console.warn('Could not store dataset for retrain version ' + nextVer);
                }
            }
        }

        saveModels(models);
        return version;
    }

    function getVersions(modelId) {
        var model = getModel(modelId);
        return model ? (model.versions || []) : [];
    }

    function updateVersion(modelId, versionNumber, updates) {
        var models = getModels();
        var model = models.find(function(m) { return m.id === modelId; });
        if (!model || !model.versions) return null;
        var version = model.versions.find(function(v) { return v.version === versionNumber; });
        if (!version) return null;
        for (var key in updates) {
            if (updates.hasOwnProperty(key)) {
                version[key] = updates[key];
            }
        }
        saveModels(models);
        return version;
    }

    var PRODUCTION_KEY = 'synthai_production_model';

    function setProductionModel(modelId) {
        try {
            localStorage.setItem(PRODUCTION_KEY, JSON.stringify(modelId));
            return true;
        } catch (e) { return false; }
    }

    function getProductionModel() {
        try {
            var id = JSON.parse(localStorage.getItem(PRODUCTION_KEY));
            if (!id) return null;
            return getModel(id);
        } catch (e) { return null; }
    }

    function unsetProductionModel() {
        try {
            localStorage.removeItem(PRODUCTION_KEY);
            return true;
        } catch (e) { return false; }
    }

    return {
        getModels: getModels,
        getModel: getModel,
        addModel: addModel,
        updateModel: updateModel,
        deleteModel: deleteModel,
        getModelDataset: getModelDataset,
        getStats: getStats,
        searchModels: searchModels,
        addGeneratedDataset: addGeneratedDataset,
        addVersion: addVersion,
        getVersions: getVersions,
        updateVersion: updateVersion,
        classifyTrainingQuality: classifyTrainingQuality,
        trainingImbalanceWarning: trainingImbalanceWarning,
        generateLossValues: generateLossValues,
        setProductionModel: setProductionModel,
        getProductionModel: getProductionModel,
        unsetProductionModel: unsetProductionModel
    };
})();
