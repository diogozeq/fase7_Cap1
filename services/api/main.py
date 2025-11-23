"""
FarmTech Consolidado - Backend API
FastAPI application entry point
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def _resolve_model_source() -> str | Path:
    """Resolve YOLO model path or hub identifier, preferring local files."""
    configured = os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt")
    candidate = Path(configured)
    project_root = Path(__file__).resolve().parents[2]

    if candidate.is_absolute() and candidate.exists():
        return candidate

    local_candidate = (project_root / candidate).resolve()
    if local_candidate.exists():
        return local_candidate

    return configured


def _resolve_static_images_dir() -> Path | None:
    """Resolve static images directory delivered in Fase 6 or via env."""
    candidates = []
    env_dir = os.getenv("CV_STATIC_IMAGES_DIR")
    if env_dir:
        candidates.append(Path(env_dir))

    project_root = Path(__file__).resolve().parents[2]
    # Prefer amostras versionadas no repositorio
    candidates.append(project_root / "models" / "cv_samples")
    # Pasta legada (caso tenha sido baixada separadamente)
    candidates.append(
        project_root.parents[2]
        / "Fase 6 - 2025"
        / "Cap 1 - Despertar da rede neural"
        / "Imagens para Demanda"
        / "test"
        / "images"
    )

    for c in candidates:
        if c.exists():
            return c
    return None


def _seed_cv_detections(app) -> None:
    """Seed detections running YOLO over static images so UI is immediately real."""
    try:
        force_reset = os.getenv("CV_SEED_RESET", "1") == "1"
        if force_reset:
            app.state.db.reset_detections()
        else:
            existing = app.state.db.get_detections(limit=1)
            if existing:
                logger.info("cv_seed_skipped", reason="detections_already_exist")
                return

        static_dir = _resolve_static_images_dir()
        if not static_dir:
            logger.warning("cv_seed_skipped", reason="static_dir_missing")
            return

        from services.core.cv_service.service import CVService

        model_source = _resolve_model_source()
        models_dir = Path(model_source).parent if isinstance(model_source, Path) else Path("./models")
        cv = CVService(models_dir=models_dir, model_source=model_source)

        conf = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", 0.35))
        limit = int(os.getenv("CV_SEED_LIMIT", 60))
        results = cv.detect_directory(static_dir, confidence=conf, limit=limit)

        saved = 0
        for img_path, detections in results.items():
            ts = img_path.stat().st_mtime
            from datetime import datetime

            for d in detections:
                det_data = {
                    "timestamp": datetime.fromtimestamp(ts),
                    "imagem_nome": img_path.name,
                    "classe": d.class_name,
                    "confianca": d.confidence,
                    "bbox": str(d.bbox),
                }
                app.state.db.create_detection(det_data)
                saved += 1

        logger.info("cv_seed_completed", images=len(results), detections=saved)
    except Exception as e:
        logger.warning("cv_seed_failed", error=str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("farmtech_api_starting", version="1.0.0")
    # Initialize database
    from services.core.database.service import DatabaseService
    from services.core.database.models import Talhao, Sensor, TipoSensor
    app.state.db = DatabaseService(os.getenv("DATABASE_URL"))
    app.state.db.create_tables()
    
    # Initialize AWS Service
    from services.core.aws_integration.service import AWSService
    app.state.aws = AWSService()

    # Basic seed for FK integrity
    try:
        with app.state.db.get_session() as s:
            if s.query(Talhao).count() == 0:
                talhao = Talhao(nome_talhao="Talhão Principal", area_hectares=10.0)
                s.add(talhao)
                s.flush()
                if s.query(TipoSensor).count() == 0:
                    tipo = TipoSensor(nome_tipo_sensor="Umidade", unidade_medida_padrao="%")
                    s.add(tipo)
                    s.flush()
                from datetime import date
                sensor = Sensor(
                    identificacao_fabricante="ESP32-001",
                    data_instalacao=date.today(),
                    id_tipo_sensor=1,
                    id_talhao=talhao.id_talhao,
                )
                s.add(sensor)
    except Exception:
        logger.warning("seed_failed")

    # Seed CV detections from static images so frontend shows real data
    _seed_cv_detections(app)
    yield
    logger.info("farmtech_api_shutdown")


# Create FastAPI application
app = FastAPI(
    title="FarmTech Consolidado API",
    description="API REST para Sistema de Gestão Agrícola Inteligente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router with /api prefix
api = APIRouter(prefix="/api")

# Include sub-routers
from services.api.routes import calculations, iot, cv, database, analytics, alerts, ml, genetic
api.include_router(calculations.router)
api.include_router(iot.router)
api.include_router(cv.router)
api.include_router(database.router)
api.include_router(analytics.router)
api.include_router(alerts.router)
api.include_router(ml.router)
api.include_router(genetic.router)

@api.get("/health")
async def api_health():
    return {"status": "healthy", "service": "farmtech-api"}

app.include_router(api)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FarmTech Consolidado API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "farmtech-api"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
