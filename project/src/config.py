import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

env_path = BASE_DIR / "configs" / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "artifacts" / "model_catboost_best_optuna.pkl"))
SCALER_PATH = os.getenv("SCALER_PATH", str(BASE_DIR / "artifacts" / "scaler_cb.pkl"))
CONFIG_PATH = os.getenv("CONFIG_PATH", str(BASE_DIR / "artifacts" / "CB_mlflow" / "catboost_optuna_config.json"))