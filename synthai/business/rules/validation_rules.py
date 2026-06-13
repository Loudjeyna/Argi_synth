"""Business Logic Layer — data validation rules (stateless)."""


class ValidationRules:
    """Stateless validation rules used by the AI Core and frontend."""

    MIN_TEMP = -10
    MAX_TEMP = 55
    MIN_PH = 0
    MAX_PH = 14
    MIN_NPK = 0
    MAX_NPK = 300
    MIN_HUMIDITY = 0
    MAX_HUMIDITY = 100
    MIN_PRESSURE = 800
    MAX_PRESSURE = 1100
    MIN_CLOUD = 0
    MAX_CLOUD = 100

    VALID_CROPS = {
        "rice", "maize", "cotton", "jute", "coffee", "banana", "mango",
        "grapes", "apple", "coconut", "chickpea", "lentil", "blackgram",
        "kidneybeans", "pigeonpeas", "muskmelon", "watermelon", "orange",
        "papaya", "pomegranate", "mungbean", "mothbeans",
    }

    VALID_SOIL_TEXTURES = {"sandy", "loam", "clay", "silt", "peat"}

    @classmethod
    def check_value(cls, value, lo, hi, name: str) -> dict:
        ok = lo <= value <= hi
        return {"name": name, "valid": ok, "value": value, "range": f"{lo}-{hi}"}

    @classmethod
    def validate_crop_row(cls, row: dict) -> list:
        checks = []
        if "N" in row:
            checks.append(cls.check_value(float(row["N"]), cls.MIN_NPK, cls.MAX_NPK, "N"))
        if "P" in row:
            checks.append(cls.check_value(float(row["P"]), cls.MIN_NPK, cls.MAX_NPK, "P"))
        if "K" in row:
            checks.append(cls.check_value(float(row["K"]), cls.MIN_NPK, cls.MAX_NPK, "K"))
        if "temperature" in row:
            checks.append(cls.check_value(float(row["temperature"]), cls.MIN_TEMP, cls.MAX_TEMP, "temperature"))
        if "humidity" in row:
            checks.append(cls.check_value(float(row["humidity"]), cls.MIN_HUMIDITY, cls.MAX_HUMIDITY, "humidity"))
        if "ph" in row:
            checks.append(cls.check_value(float(row["ph"]), cls.MIN_PH, cls.MAX_PH, "ph"))
        if "rainfall" in row:
            checks.append(cls.check_value(float(row["rainfall"]), 0, 500, "rainfall"))
        if "label" in row and row["label"]:
            checks.append({
                "name": "crop_label",
                "valid": row["label"].lower() in cls.VALID_CROPS,
                "value": row["label"],
                "range": "22 valid crops",
            })
        if "texture" in row and row["texture"]:
            checks.append({
                "name": "soil_texture",
                "valid": row["texture"].lower() in cls.VALID_SOIL_TEXTURES,
                "value": row["texture"],
                "range": "5 valid textures",
            })
        return checks
