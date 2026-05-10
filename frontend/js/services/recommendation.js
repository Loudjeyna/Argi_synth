/* SynthAI - Recommendation Engine */
const RecommendationService = (function() {
    // Crop statistics based on Crop_recommendation.csv
    const cropData = {
        rice: { n:[45,105], p:[35,65], k:[35,55], temp:[20,35], humidity:[70,95], ph:[5,7], rainfall:[100,350], water:"High", fertilizer:"Medium" },
        maize: { n:[55,110], p:[40,85], k:[25,65], temp:[18,35], humidity:[55,85], ph:[5,7], rainfall:[50,200], water:"Medium", fertilizer:"High" },
        cotton: { n:[50,125], p:[40,90], k:[25,55], temp:[20,40], humidity:[50,80], ph:[5,8], rainfall:[50,180], water:"Medium", fertilizer:"High" },
        jute: { n:[75,120], p:[30,85], k:[30,80], temp:[20,38], humidity:[70,90], ph:[6,7], rainfall:[150,300], water:"High", fertilizer:"Medium" },
        coffee: { n:[50,110], p:[40,80], k:[25,55], temp:[18,30], humidity:[65,85], ph:[5,7], rainfall:[100,300], water:"Medium", fertilizer:"Medium" },
        banana: { n:[70,120], p:[45,90], k:[30,70], temp:[25,38], humidity:[70,90], ph:[5,7], rainfall:[100,250], water:"High", fertilizer:"High" },
        mango: { n:[35,90], p:[25,70], k:[20,55], temp:[20,38], humidity:[50,85], ph:[5,7], rainfall:[50,200], water:"Low", fertilizer:"Medium" },
        grapes: { n:[40,100], p:[35,80], k:[25,55], temp:[15,35], humidity:[45,75], ph:[5,7], rainfall:[50,150], water:"Low", fertilizer:"Medium" },
        apple: { n:[30,80], p:[25,60], k:[20,45], temp:[5,20], humidity:[50,80], ph:[5,7], rainfall:[100,200], water:"Medium", fertilizer:"Low" },
        coconut: { n:[40,90], p:[30,70], k:[25,55], temp:[25,35], humidity:[70,95], ph:[5,8], rainfall:[150,350], water:"High", fertilizer:"Medium" },
        chickpea: { n:[30,80], p:[35,75], k:[20,50], temp:[15,30], humidity:[40,70], ph:[6,8], rainfall:[50,150], water:"Low", fertilizer:"Low" },
        lentil: { n:[25,70], p:[30,65], k:[20,45], temp:[10,30], humidity:[40,70], ph:[5,7], rainfall:[50,150], water:"Low", fertilizer:"Low" },
        blackgram: { n:[20,60], p:[25,60], k:[15,40], temp:[20,35], humidity:[50,75], ph:[6,8], rainfall:[50,150], water:"Low", fertilizer:"Low" },
        kidneybeans: { n:[35,80], p:[30,70], k:[20,50], temp:[15,30], humidity:[45,70], ph:[5,7], rainfall:[50,150], water:"Low", fertilizer:"Medium" },
        pigeonpeas: { n:[30,70], p:[25,60], k:[20,45], temp:[20,35], humidity:[50,75], ph:[5,8], rainfall:[50,150], water:"Low", fertilizer:"Low" },
        muskmelon: { n:[40,90], p:[30,70], k:[25,55], temp:[20,35], humidity:[60,85], ph:[5,7], rainfall:[100,250], water:"Medium", fertilizer:"Medium" },
        watermelon: { n:[45,100], p:[35,75], k:[30,65], temp:[20,35], humidity:[60,85], ph:[5,7], rainfall:[100,250], water:"Medium", fertilizer:"Medium" },
        orange: { n:[35,80], p:[25,65], k:[20,50], temp:[15,35], humidity:[50,80], ph:[5,7], rainfall:[100,200], water:"Medium", fertilizer:"Medium" },
        papaya: { n:[40,90], p:[30,70], k:[25,55], temp:[20,35], humidity:[60,85], ph:[5,7], rainfall:[100,250], water:"Medium", fertilizer:"Medium" },
        pomegranate: { n:[35,80], p:[25,60], k:[20,50], temp:[15,35], humidity:[40,70], ph:[5,7], rainfall:[50,200], water:"Low", fertilizer:"Low" },
        mungbean: { n:[25,65], p:[25,60], k:[15,40], temp:[20,35], humidity:[50,75], ph:[6,8], rainfall:[50,150], water:"Low", fertilizer:"Low" },
        mothbeans: { n:[20,55], p:[20,55], k:[15,35], temp:[20,35], humidity:[45,70], ph:[6,8], rainfall:[50,150], water:"Low", fertilizer:"Low" }
    };

    function getCrops() {
        return Object.keys(cropData);
    }

    function getCropConditions(crop) {
        return cropData[crop.toLowerCase()] || null;
    }

    function getCropRecommendation(crop) {
        const conditions = getCropConditions(crop);
        if (!conditions) return null;
        return {
            crop: crop.charAt(0).toUpperCase() + crop.slice(1),
            optimal_n: conditions.n[0] + " - " + conditions.n[1],
            optimal_p: conditions.p[0] + " - " + conditions.p[1],
            optimal_k: conditions.k[0] + " - " + conditions.k[1],
            optimal_temperature: conditions.temp[0] + "C - " + conditions.temp[1] + "C",
            optimal_humidity: conditions.humidity[0] + "% - " + conditions.humidity[1] + "%",
            optimal_ph: conditions.ph[0] + " - " + conditions.ph[1],
            optimal_rainfall: conditions.rainfall[0] + "mm - " + conditions.rainfall[1] + "mm",
            water_level: conditions.water,
            fertilizer_level: conditions.fertilizer
        };
    }

    function predictCrop(conditions) {
        const crops = getCrops();
        const scores = crops.map(crop => {
            const data = cropData[crop];
            let score = 0;
            score += Math.abs(conditions.n - (data.n[0] + data.n[1]) / 2) / 100;
            score += Math.abs(conditions.p - (data.p[0] + data.p[1]) / 2) / 100;
            score += Math.abs(conditions.k - (data.k[0] + data.k[1]) / 2) / 200;
            score += Math.abs(conditions.temperature - (data.temp[0] + data.temp[1]) / 2) / 50;
            score += Math.abs(conditions.humidity - (data.humidity[0] + data.humidity[1]) / 2) / 100;
            score += Math.abs(conditions.ph - (data.ph[0] + data.ph[1]) / 2) / 10;
            score += Math.abs(conditions.rainfall - (data.rainfall[0] + data.rainfall[1]) / 2) / 350;
            return { crop: crop.charAt(0).toUpperCase() + crop.slice(1), match: Math.max(0, Math.round(100 - score * 50)) };
        });
        scores.sort((a, b) => b.match - a.match);
        return scores.slice(0, 5).map((item, idx) => ({
            rank: idx + 1, crop: item.crop, match_score: item.match + "%",
            water_level: cropData[item.crop.toLowerCase()].water,
            fertilizer_level: cropData[item.crop.toLowerCase()].fertilizer
        }));
    }

    function exportResults(results, type) {
        let csv;
        if (type === 'conditions') {
            csv = "Parameter,Value\n" + Object.entries(results).map(([k,v]) => `${k},"${v}"`).join('\n');
        } else {
            csv = "Rank,Crop,Match Score,Water Level,Fertilizer Level\n" + results.map(r => `${r.rank},"${r.crop}","${r.match_score}","${r.water_level}","${r.fertilizer_level}"`).join('\n');
        }
        const blob = new Blob(["\ufeff" + csv], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "recommendations.csv";
        a.click();
        URL.revokeObjectURL(url);
    }

    return { getCrops, getCropConditions, getCropRecommendation, predictCrop, exportResults };
})();