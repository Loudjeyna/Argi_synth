/* SynthAI - History Service */
const HistoryService = (function() {
    const HISTORY_KEY = 'synthai_history';

    function getHistory(userId = null) {
        const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
        return userId ? history.filter(h => h.userId === userId).sort((a,b) => b.timestamp - a.timestamp) : history;
    }

    function addEntry(entry) {
        const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
        entry.id = Date.now();
        entry.timestamp = Date.now();
        entry.date = new Date().toISOString();
        history.push(entry);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
        return entry;
    }

    function getUserHistory(userId, limit = null) {
        let history = getHistory(userId);
        return limit ? history.slice(0, limit) : history;
    }

    function getRecent(userId, limit = 10) {
        return getUserHistory(userId, limit);
    }

    function searchByCrop(userId, crop) {
        const history = getUserHistory(userId);
        return history.filter(h => h.crop && h.crop.toLowerCase().includes(crop.toLowerCase()));
    }

    function filterByDate(userId, dateStr) {
        const history = getUserHistory(userId);
        return history.filter(h => h.date && h.date.startsWith(dateStr));
    }

    function deleteEntry(id) {
        let history = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
        history = history.filter(h => h.id !== id);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    }

    function exportHistory(userId) {
        const history = getUserHistory(userId);
        const csvContent = "data:text/csv;charset=utf-8," +
            "Type,Input,Result,Date\n" +
            history.map(h => {
                return `${h.type},"${h.input}","${h.result}","${h.date}"`;
            }).join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "prediction_history.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    function getStats(userId) {
        const history = getUserHistory(userId);
        return {
            totalPredictions: history.length,
            cropRecommendations: history.filter(h => h.type === 'crop_conditions').length,
            conditionPredictions: history.filter(h => h.type === 'conditions_crop').length,
            dataGenerations: history.filter(h => h.type === 'data_generation').length,
            lastPrediction: history.length > 0 ? history[0].date : 'N/A'
        };
    }

    return { getHistory, addEntry, getUserHistory, getRecent, searchByCrop, filterByDate, deleteEntry, exportHistory, getStats };
})();