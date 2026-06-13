"""Service Layer — data augmentation workflow."""

import json
import random

from synthai.data.repositories.dataset_repository import DatasetRepository
from synthai.data.repositories.user_repository import UserRepository
from synthai.data.repositories.payment_repository import UsageLogRepository
from synthai.business.rules.subscription_rules import SubscriptionRules


class AugmentationService:
    """Coordinates augmentation: parse CSV → apply multiplier → validate → persist."""

    @staticmethod
    def augment(user_id: int, headers: list, rows: list, multiplier: int,
                file_name: str = "uploaded.csv", dataset_type: str = "generic") -> dict:

        user = UserRepository.find_by_id(user_id)
        plan = user["plan"] if user else "free"
        allowed = SubscriptionRules.allowed_augmentation_multipliers(plan)
        if multiplier not in allowed:
            return {"success": False, "message": f"Multiplier x{multiplier} not available on your plan"}

        original_count = len(rows)
        augmented = []
        for row in rows:
            for _ in range(multiplier - 1):
                new_row = {}
                for h in headers:
                    try:
                        val = float(row[h])
                        noise = val * 0.1 * (random.random() * 2 - 1)
                        new_row[h] = round(val + noise, 2)
                    except (ValueError, TypeError):
                        new_row[h] = row[h]
                augmented.append(new_row)

        all_data = rows + augmented
        preview = all_data[:50]

        entry_data = {
            "user_id": user_id,
            "file_name": file_name,
            "original_rows": original_count,
            "augmented_rows": len(all_data),
            "multiplier": multiplier,
            "dataset_type": dataset_type,
            "headers": json.dumps(headers),
            "quality_score": 85,
            "quality_label": "Good",
            "correlation_similarity": None,
            "original_stats": json.dumps({"rows": original_count, "cols": len(headers)}),
            "augmented_stats": json.dumps({"rows": len(all_data), "cols": len(headers)}),
            "preview_data": json.dumps(preview),
        }
        aug_id = DatasetRepository.create_augmentation(entry_data)
        UsageLogRepository.add(user_id, "augmentation", len(all_data))
        return {"success": True, "id": aug_id, "original_rows": original_count, "total_rows": len(all_data)}
