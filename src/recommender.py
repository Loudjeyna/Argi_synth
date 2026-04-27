import pandas as pd
import numpy as np
from typing import Dict, Optional
from pathlib import Path


class CropRecommender:
    """Crop recommendation system based on dataset statistics."""
    
    CROP_DATA_PATH = "data/Crop_recommendation.csv"
    _instance = None
    _df = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._df is None:
            self._load_data()
    
    def _load_data(self):
        """Load crop data."""
        if Path(self.CROP_DATA_PATH).exists():
            self._df = pd.read_csv(self.CROP_DATA_PATH)
            self._df['label'] = self._df['label'].str.lower()
    
    def get_all_crops(self) -> list:
        """Get all available crops."""
        if self._df is not None:
            return sorted(self._df['label'].unique().tolist())
        return []
    
    def get_crop_stats(self, crop_name: str) -> Optional[Dict]:
        """Get statistics for a specific crop."""
        if self._df is None:
            return None
        
        crop_data = self._df[self._df['label'] == crop_name.lower()]
        if crop_data.empty:
            return None
        
        stats = {
            "crop": crop_name,
            "sample_count": len(crop_data),
            "temperature": {
                "min": round(crop_data['temperature'].min(), 2),
                "max": round(crop_data['temperature'].max(), 2),
                "mean": round(crop_data['temperature'].mean(), 2),
                "optimal_min": round(crop_data['temperature'].quantile(0.25), 2),
                "optimal_max": round(crop_data['temperature'].quantile(0.75), 2)
            },
            "humidity": {
                "min": round(crop_data['humidity'].min(), 2),
                "max": round(crop_data['humidity'].max(), 2),
                "mean": round(crop_data['humidity'].mean(), 2),
                "optimal_min": round(crop_data['humidity'].quantile(0.25), 2),
                "optimal_max": round(crop_data['humidity'].quantile(0.75), 2)
            },
            "ph": {
                "min": round(crop_data['ph'].min(), 2),
                "max": round(crop_data['ph'].max(), 2),
                "mean": round(crop_data['ph'].mean(), 2),
                "optimal_min": round(crop_data['ph'].quantile(0.25), 2),
                "optimal_max": round(crop_data['ph'].quantile(0.75), 2)
            },
            "rainfall": {
                "min": round(crop_data['rainfall'].min(), 2),
                "max": round(crop_data['rainfall'].max(), 2),
                "mean": round(crop_data['rainfall'].mean(), 2),
                "optimal_min": round(crop_data['rainfall'].quantile(0.25), 2),
                "optimal_max": round(crop_data['rainfall'].quantile(0.75), 2)
            },
            "N": {
                "mean": round(crop_data['N'].mean(), 2),
                "optimal_min": round(crop_data['N'].quantile(0.25), 2),
                "optimal_max": round(crop_data['N'].quantile(0.75), 2)
            },
            "P": {
                "mean": round(crop_data['P'].mean(), 2),
                "optimal_min": round(crop_data['P'].quantile(0.25), 2),
                "optimal_max": round(crop_data['P'].quantile(0.75), 2)
            },
            "K": {
                "mean": round(crop_data['K'].mean(), 2),
                "optimal_min": round(crop_data['K'].quantile(0.25), 2),
                "optimal_max": round(crop_data['K'].quantile(0.75), 2)
            }
        }
        
        stats["water_level"] = self._determine_water_level(crop_data['rainfall'].mean())
        stats["fertilizer_level"] = self._determine_fertilizer_level(
            crop_data['N'].mean(), crop_data['P'].mean(), crop_data['K'].mean()
        )
        
        return stats
    
    def _determine_water_level(self, rainfall: float) -> str:
        """Determine water level requirement."""
        if rainfall > 200:
            return "High"
        elif rainfall > 100:
            return "Medium"
        else:
            return "Low"
    
    def _determine_fertilizer_level(self, N: float, P: float, K: float) -> str:
        """Determine fertilizer requirement."""
        avg = (N + P + K) / 3
        if avg > 80:
            return "High"
        elif avg > 40:
            return "Medium"
        else:
            return "Low"
    
    def get_recommendation(self, crop_name: str) -> Dict:
        """Get formatted recommendation for a crop."""
        stats = self.get_crop_stats(crop_name)
        
        if not stats:
            return {}
        
        return {
            "crop": stats["crop"].title(),
            "optimal_temperature": f"{stats['temperature']['optimal_min']}°C - {stats['temperature']['optimal_max']}°C",
            "optimal_humidity": f"{stats['humidity']['optimal_min']}% - {stats['humidity']['optimal_max']}%",
            "optimal_ph": f"{stats['ph']['optimal_min']} - {stats['ph']['optimal_max']}",
            "optimal_rainfall": f"{stats['rainfall']['optimal_min']}mm - {stats['rainfall']['optimal_max']}mm",
            "water_level": stats["water_level"],
            "fertilizer_level": stats["fertilizer_level"],
            "nitrogen_required": f"{stats['N']['optimal_min']} - {stats['N']['optimal_max']}",
            "phosphorus_required": f"{stats['P']['optimal_min']} - {stats['P']['optimal_max']}",
            "potassium_required": f"{stats['K']['optimal_min']} - {stats['K']['optimal_max']}"
        }
    
    def get_all_recommendations(self) -> pd.DataFrame:
        """Get all crop recommendations as DataFrame."""
        if self._df is None:
            return pd.DataFrame()
        
        crops = self.get_all_crops()
        recommendations = []
        
        for crop in crops:
            stats = self.get_crop_stats(crop)
            if stats:
                recommendations.append({
                    "Crop": stats["crop"].title(),
                    "Temperature (°C)": f"{stats['temperature']['optimal_min']} - {stats['temperature']['optimal_max']}",
                    "Humidity (%)": f"{stats['humidity']['optimal_min']} - {stats['humidity']['optimal_max']}",
                    "pH Range": f"{stats['ph']['optimal_min']} - {stats['ph']['optimal_max']}",
                    "Rainfall (mm)": f"{stats['rainfall']['optimal_min']} - {stats['rainfall']['optimal_max']}",
                    "Water Level": stats["water_level"],
                    "Fertilizer": stats["fertilizer_level"]
                })
        
        return pd.DataFrame(recommendations)