import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from data import ClientProfile, PredictionResponse
from model import model_service
from config import APP_HOST, APP_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Credit Limit Prediction API",
    description="Сервис прогнозирования кредитного лимита на основе профиля клиента.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Загружаем модель при старте сервиса"""
    logger.info("Starting up service...")
    try:
        model_service.load_artifacts()
        logger.info("Service is ready to accept requests.")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}")

@app.get("/health")
async def health_check():
    """Endpoint для проверки работоспособности сервиса"""
    if model_service.is_loaded:
        return {"status": "healthy", "model_loaded": True}
    else:
        return {"status": "unhealthy", "model_loaded": False}

@app.post("/predict", response_model=PredictionResponse)
async def predict_credit_limit(profiles: List[ClientProfile]):
    """
    Принимает список профилей клиентов и возвращает прогнозируемый кредитный лимит.
    
    - **profiles**: Список объектов ClientProfile.
    """
    try:
        features = [p.dict() for p in profiles]
        
        predictions = model_service.predict(features)
        
        if len(predictions) == 1:
            return PredictionResponse(predicted_credit_limit=float(predictions[0]))

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {APP_HOST}:{APP_PORT}")
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)