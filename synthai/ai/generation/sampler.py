"""AI Core Layer — non-ML synthetic data bootstrapping."""

import uuid
from typing import Optional
import pandas as pd

from synthai.data.config.settings import GENERATED_DIR, CROP_CSV_PATH


class SimpleSampler:
    """Generates synthetic data via bootstrap resampling (no trained model needed).

    Used by GenerationService as a lightweight fallback when no CTGAN model
    has been trained, keeping ML-agnostic sampling logic in the AI layer.
    """

    @staticmethod
    def sample(num_rows: int = 1000,
               source_path: Optional[str] = None,
               output_dir: Optional[str] = None) -> dict:
        source = source_path or str(CROP_CSV_PATH)
        out_dir = output_dir or str(GENERATED_DIR)
        real_df = pd.read_csv(source)
        synth_df = real_df.sample(n=min(num_rows, len(real_df)), replace=True).reset_index(drop=True)

        file_name = f"dataset_{uuid.uuid4().hex[:8]}.csv"
        csv_path = f"{out_dir}/{file_name}"
        synth_df.to_csv(csv_path, index=False)

        headers = list(synth_df.columns)
        preview = synth_df.head(50).to_dict(orient="records")

        return {
            "synth_df": synth_df,
            "headers": headers,
            "preview": preview,
            "file_path": csv_path,
        }
