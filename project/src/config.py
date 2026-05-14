import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл, если он есть (для локальной разработки)
load_dotenv()

# Базовая директория проекта (поднимаемся из src/ в корень project/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Пути к артефактам (берем из env или используем дефолтные)
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "artifacts" / "model_catboost_best_optuna.pkl"))
SCALER_PATH = os.getenv("SCALER_PATH", str(BASE_DIR / "artifacts" / "scaler_cb.pkl"))
CONFIG_PATH = os.getenv("CONFIG_PATH", str(BASE_DIR / "artifacts" / "CB_mlflow" / "catboost_optuna_config.json"))

# Настройки сервера
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))