/* SynthAI - Recommendation Engine (Algerian Agriculture) */
const RecommendationService = (function() {
    // Crop statistics adapted for Algerian climate and agricultural environment
    var cropData = {
        ble_dur:       { n:[40,100], p:[30,70],  k:[25,55],  temp:[10,30], humidity:[40,65], ph:[6,8],   rainfall:[80,200], water:"Medium", fertilizer:"High" },
        orge:          { n:[35,90],  p:[25,60],  k:[20,50],  temp:[8,28],  humidity:[35,60], ph:[6,8],   rainfall:[60,180], water:"Low",    fertilizer:"Medium" },
        dattes:        { n:[25,70],  p:[20,55],  k:[25,50],  temp:[25,45], humidity:[15,35], ph:[7,9],   rainfall:[5,80],   water:"Low",    fertilizer:"Low" },
        zitoun:        { n:[25,75],  p:[20,60],  k:[20,50],  temp:[12,32], humidity:[40,70], ph:[6,8],   rainfall:[80,200], water:"Low",    fertilizer:"Medium" },
        oranges:       { n:[35,80],  p:[25,65],  k:[20,50],  temp:[15,35], humidity:[50,80], ph:[5,7],   rainfall:[100,200],water:"Medium", fertilizer:"Medium" },
        aneb:          { n:[40,100], p:[35,80],  k:[25,55],  temp:[15,35], humidity:[45,75], ph:[5,7],   rainfall:[50,150], water:"Low",    fertilizer:"Medium" },
        karmous:       { n:[30,80],  p:[25,60],  k:[20,50],  temp:[18,35], humidity:[45,70], ph:[6,8],   rainfall:[60,180], water:"Medium", fertilizer:"Medium" },
        rouman:        { n:[35,80],  p:[25,60],  k:[20,50],  temp:[15,35], humidity:[40,70], ph:[5,7],   rainfall:[50,200], water:"Low",    fertilizer:"Low" },
        homos:         { n:[30,80],  p:[35,75],  k:[20,50],  temp:[15,30], humidity:[40,70], ph:[6,8],   rainfall:[50,150], water:"Low",    fertilizer:"Low" },
        adas:          { n:[25,70],  p:[30,65],  k:[20,45],  temp:[10,30], humidity:[40,70], ph:[5,7],   rainfall:[50,150], water:"Low",    fertilizer:"Low" },
        batata:        { n:[50,110], p:[35,75],  k:[40,80],  temp:[15,28], humidity:[50,75], ph:[5,6],   rainfall:[80,200], water:"Medium", fertilizer:"High" },
        tomatish:      { n:[45,105], p:[35,70],  k:[30,65],  temp:[18,32], humidity:[55,80], ph:[5,7],   rainfall:[80,200], water:"Medium", fertilizer:"High" },
        bsla:          { n:[30,80],  p:[25,60],  k:[20,50],  temp:[12,28], humidity:[50,75], ph:[6,7],   rainfall:[80,180], water:"Medium", fertilizer:"Medium" },
        dellaa:        { n:[45,100], p:[35,75],  k:[30,65],  temp:[20,35], humidity:[60,85], ph:[5,7],   rainfall:[100,250],water:"Medium", fertilizer:"Medium" },
        bettikh:       { n:[40,90],  p:[30,70],  k:[25,55],  temp:[20,35], humidity:[60,85], ph:[5,7],   rainfall:[100,250],water:"Medium", fertilizer:"Medium" },
        felfel:        { n:[40,95],  p:[30,70],  k:[25,55],  temp:[18,32], humidity:[55,80], ph:[5,7],   rainfall:[80,200], water:"Medium", fertilizer:"High" },
        zroudiya:      { n:[30,80],  p:[25,60],  k:[30,70],  temp:[10,25], humidity:[45,70], ph:[5,7],   rainfall:[80,180], water:"Medium", fertilizer:"Medium" },
        jelbana:       { n:[20,60],  p:[25,60],  k:[15,40],  temp:[10,25], humidity:[45,70], ph:[6,8],   rainfall:[50,150], water:"Low",    fertilizer:"Low" },
        michmich:      { n:[30,80],  p:[25,60],  k:[20,50],  temp:[15,32], humidity:[45,70], ph:[6,8],   rainfall:[60,180], water:"Medium", fertilizer:"Medium" },
        louz:          { n:[25,70],  p:[20,55],  k:[20,50],  temp:[8,28],  humidity:[40,65], ph:[6,8],   rainfall:[60,180], water:"Low",    fertilizer:"Low" },
        maize:         { n:[55,110], p:[40,85],  k:[25,65],  temp:[18,35], humidity:[55,85], ph:[5,7],   rainfall:[50,200], water:"Medium", fertilizer:"High" },
        tournesol:     { n:[40,100], p:[35,80],  k:[25,60],  temp:[15,32], humidity:[45,70], ph:[6,8],   rainfall:[60,180], water:"Medium", fertilizer:"Medium" }
    };

    var cropNames = {
        ble_dur: "Durum Wheat",
        orge: "Barley",
        dattes: "Dates",
        zitoun: "Olives",
        oranges: "Oranges",
        aneb: "Grapes",
        karmous: "Figs",
        rouman: "Pomegranate",
        homos: "Chickpeas",
        adas: "Lentils",
        batata: "Potatoes",
        tomatish: "Tomatoes",
        bsla: "Onions",
        dellaa: "Watermelon",
        bettikh: "Melon",
        felfel: "Peppers",
        zroudiya: "Carrots",
        jelbana: "Peas",
        michmich: "Apricots",
        louz: "Almonds",
        maize: "Maize",
        tournesol: "Sunflower"
    };

    function getCrops() {
        return Object.keys(cropData);
    }

    function getCropDisplayName(key) {
        return cropNames[key] || key.charAt(0).toUpperCase() + key.slice(1);
    }

    function getCropConditions(crop) {
        return cropData[crop.toLowerCase()] || null;
    }

    function getCropRecommendation(crop) {
        var conditions = getCropConditions(crop);
        if (!conditions) return null;
        return {
            crop: getCropDisplayName(crop),
            optimal_n: conditions.n[0] + " - " + conditions.n[1],
            optimal_p: conditions.p[0] + " - " + conditions.p[1],
            optimal_k: conditions.k[0] + " - " + conditions.k[1],
            optimal_temperature: conditions.temp[0] + "\u00b0C - " + conditions.temp[1] + "\u00b0C",
            optimal_humidity: conditions.humidity[0] + "% - " + conditions.humidity[1] + "%",
            optimal_ph: conditions.ph[0] + " - " + conditions.ph[1],
            optimal_rainfall: conditions.rainfall[0] + "mm - " + conditions.rainfall[1] + "mm",
            water_level: conditions.water,
            fertilizer_level: conditions.fertilizer
        };
    }

    function predictCrop(conditions) {
        var crops = getCrops();
        var scores = crops.map(function(crop) {
            var data = cropData[crop];
            var score = 0;
            score += Math.abs(conditions.n - (data.n[0] + data.n[1]) / 2) / 100;
            score += Math.abs(conditions.p - (data.p[0] + data.p[1]) / 2) / 100;
            score += Math.abs(conditions.k - (data.k[0] + data.k[1]) / 2) / 200;
            score += Math.abs(conditions.temperature - (data.temp[0] + data.temp[1]) / 2) / 50;
            score += Math.abs(conditions.humidity - (data.humidity[0] + data.humidity[1]) / 2) / 100;
            score += Math.abs(conditions.ph - (data.ph[0] + data.ph[1]) / 2) / 10;
            score += Math.abs(conditions.rainfall - (data.rainfall[0] + data.rainfall[1]) / 2) / 350;
            return { crop: crop, displayName: getCropDisplayName(crop), match: Math.max(0, Math.round(100 - score * 50)) };
        });
        scores.sort(function(a, b) { return b.match - a.match; });
        return scores.slice(0, 5).map(function(item, idx) {
            return {
                rank: idx + 1,
                crop: item.displayName,
                match_score: item.match + "%",
                water_level: cropData[item.crop].water,
                fertilizer_level: cropData[item.crop].fertilizer
            };
        });
    }

    function exportResults(results, type) {
        var csv;
        if (type === 'conditions') {
            csv = "Parameter,Value\n" + Object.entries(results).map(function(e) { return e[0] + ',\"' + e[1] + '\"'; }).join('\n');
        } else {
            csv = "Rank,Crop,Match Score,Water Level,Fertilizer Level\n" + results.map(function(r) { return r.rank + ',\"' + r.crop + '\",\"' + r.match_score + '\",\"' + r.water_level + '\",\"' + r.fertilizer_level + '\"'; }).join('\n');
        }
        var blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = "recommendations.csv";
        a.click();
        URL.revokeObjectURL(url);
    }

    return { getCrops, getCropConditions, getCropRecommendation, predictCrop, exportResults, getCropDisplayName, cropNames: cropNames };
})();
