import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Создаём папку для логов, если нет
Path("logs").mkdir(exist_ok=True)

def setup_logger(name="api", log_file="logs/api.log", level=logging.INFO):
    """Настраивает логгер с выводом в файл и консоль"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Чтобы не дублировать хендлеры при перезагрузке модуля
    if not logger.handlers:
        # Файловый хендлер
        fh = logging.FileHandler(log_file, encoding="utf-8", mode="a")
        fh.setLevel(level)
        # Консольный хендлер
        ch = logging.StreamHandler()
        ch.setLevel(level)
        
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger

def save_metrics(metrics: dict, path="logs/metrics.json"):
    """Сохраняет метрики в JSON с добавлением таймстампа"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    metrics["timestamp"] = datetime.now().isoformat()
    
    # Читаем старые метрики и добавляем новые (простой лог)
    try:
        with open(path, "r", encoding="utf-8") as f:
            all_metrics = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_metrics = []
    
    all_metrics.append(metrics)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2, ensure_ascii=False)
    
    logging.getLogger("api").info(f"Метрики сохранены в {path}")

# Простой счётчик запросов в памяти (для минимума)
_request_counter = {"total": 0, "by_endpoint": {}, "by_status": {}}
_request_timings = []

def count_request(endpoint: str, status: int, duration: float):
    """Простой счётчик: увеличивает счётчики и запоминает время"""
    _request_counter["total"] += 1
    _request_counter["by_endpoint"][endpoint] = _request_counter["by_endpoint"].get(endpoint, 0) + 1
    _request_counter["by_status"][status] = _request_counter["by_status"].get(status, 0) + 1
    _request_timings.append(duration)

def get_metrics_summary():
    """Возвращает сводку по метрикам (для /metrics эндпоинта)"""
    avg_duration = sum(_request_timings) / len(_request_timings) if _request_timings else 0
    return {
        "total_requests": _request_counter["total"],
        "by_endpoint": _request_counter["by_endpoint"],
        "by_status": _request_counter["by_status"],
        "avg_response_time_sec": round(avg_duration, 4)
    }