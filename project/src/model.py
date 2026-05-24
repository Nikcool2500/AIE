import joblib
import pandas as pd
import numpy as np
import json
from typing import List, Dict
from config import MODEL_PATH, SCALER_PATH, CONFIG_PATH

class CreditLimitModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.config = None
        self.is_loaded = False
        self.cols_to_log = ['Total_Revolving_Bal', 'Total_Amt_Chng_Q4_Q1', 'Total_Trans_Amt', 'Total_Ct_Chng_Q4_Q1', 'Avg_Utilization_Ratio']

    def load_artifacts(self):
        """Загружает модель, scaler и конфигурацию в память"""
        try:
            print(f"Loading config from {CONFIG_PATH}...")
            with open(CONFIG_PATH, 'r') as f:
                self.config = json.load(f)

            print(f"Loading model from {MODEL_PATH}...")
            self.model = joblib.load(MODEL_PATH)

            print(f"Loading scaler from {SCALER_PATH}...")
            self.scaler = joblib.load(SCALER_PATH)

            self.is_loaded = True
            print("✅ All artifacts loaded successfully.")
        except FileNotFoundError as e:
            raise RuntimeError(f"Artifact not found: {e}. Check your .env or paths in config.py")

    def predict(self, features: List[Dict]) -> List[float]:
        """
        Предсказание для CatBoost модели.

        Логика обработки:
        1. Создание DataFrame из признаков
        2. Применение log1p к определённым колонкам
        3. Масштабирование числовых признаков
        4. Предсказание с помощью CatBoost

        Args:
            features: Список словарей с признаками

        Returns:
            Список предсказаний
        """
        if not self.is_loaded:
            self.load_artifacts()

        df_input = pd.DataFrame(features)

        num_cols = self.config.get('num_cols', [])
        cat_cols = self.config.get('cat_cols', [])

        all_cols = num_cols + cat_cols
        for col in all_cols:
            if col not in df_input.columns:
                raise ValueError(f"Missing required column: {col}")

        df_prepared = df_input.copy()
        for col in self.cols_to_log:
            if col in df_prepared.columns:
                df_prepared[col] = np.log1p(df_prepared[col])

        if num_cols:
            df_prepared[num_cols] = self.scaler.transform(df_prepared[num_cols])

        predictions = self.model.predict(df_prepared)

        return predictions.tolist()

model_service = CreditLimitModel()