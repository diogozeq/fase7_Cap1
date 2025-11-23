from datetime import datetime
import os
import shutil
import tempfile
from pathlib import Path
from typing import Union

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
import structlog

from services.core.cv_service.service import CVService

logger = structlog.get_logger()

router = APIRouter(prefix="/cv", tags=["Fase 6 - Visao Computacional"])


def _resolve_model_source() -> Union[Path, str]:
    """Resolve YOLO model path or hub identifier, preferring local files."""
    configured = os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt")
    candidate = Path(configured)
    project_root = Path(__file__).resolve().parents[3]

    if candidate.is_absolute() and candidate.exists():
        return candidate

    local_candidate = (project_root / candidate).resolve()
    if local_candidate.exists():
        return local_candidate

    # Keep the raw value so Ultralytics can download from hub if needed
    return configured


def _resolve_static_images_dir() -> Path:
    """Resolve the directory with static images used to feed the detector."""
    candidates = []

    env_dir = os.getenv("CV_STATIC_IMAGES_DIR")
    if env_dir:
        candidates.append(Path(env_dir))

    project_root = Path(__file__).resolve().parents[3]

    # In-repo amostras sempre presentes neste pacote
    candidates.append(project_root / "models" / "cv_samples")

    # Pasta legada da fase 6 (caso exista como irmao deste repositorio)
    candidates.append(
        project_root.parents[2]
        / "Fase 6 - 2025"
        / "Cap 1 - Despertar da rede neural"
        / "Imagens para Demanda"
        / "test"
        / "images"
    )

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    raise FileNotFoundError("Nenhum diretorio de imagens estaticas encontrado.")


@router.get("/status")
async def cv_status():
    """Expose current CV configuration so the frontend can show real status."""
    try:
        static_dir = str(_resolve_static_images_dir())
    except Exception:
        static_dir = None

    model_source = _resolve_model_source()
    return {
        "model_source": str(model_source),
        "static_images_dir": static_dir,
        "default_confidence": float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", 0.35)),
    }


@router.post("/analyze")
async def analyze_image(request: Request, file: UploadFile = File(...), confidence: float = 0.5):
    """Run YOLO on an uploaded image and persist the detections."""
    try:
        model_source = _resolve_model_source()
        models_dir = Path(model_source).parent if isinstance(model_source, Path) else Path("./models")
        cv = CVService(models_dir=models_dir, model_source=model_source)

        # Save uploaded file to temp
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

        try:
            detections = cv.detect_objects(tmp_path, confidence=confidence)

            for d in detections:
                try:
                    det_data = {
                        "timestamp": datetime.now(),
                        "imagem_nome": file.filename,
                        "classe": d.class_name,
                        "confianca": d.confidence,
                        "bbox": str(d.bbox),
                    }
                    request.app.state.db.create_detection(det_data)
                except Exception as e:
                    logger.warning("save_detection_failed", error=str(e))

            # Trigger AWS Alert if detections found (kept, but AWS ignored if not configured)
            if detections and hasattr(request.app.state, "aws"):
                try:
                    det_summary = ", ".join([f"{d.class_name} ({d.confidence:.2f})" for d in detections])
                    message = f"ALERTA VISAO COMPUTACIONAL: Objetos detectados na imagem {file.filename}: {det_summary}"
                    topic_arn = os.getenv("AWS_SNS_TOPIC_ARN", "")
                    if topic_arn:
                        request.app.state.aws.send_alert(
                            topic_arn=topic_arn, message=message, subject="FarmTech CV Alert"
                        )
                except Exception as e:
                    logger.warning("send_alert_failed", error=str(e))

            return [
                {
                    "class": d.class_name,
                    "confidence": d.confidence,
                    "bbox": d.bbox,
                    "image": file.filename,
                }
                for d in detections
            ]
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest-static")
async def ingest_static_images(request: Request, confidence: float = 0.35, limit: int = 25, reset: bool = True):
    """
    Processa um lote de imagens estaticas (ex: pasta da Fase 6) para popular o historico
    com deteccoes reais executadas pelo YOLO.
    """
    try:
        static_dir = _resolve_static_images_dir()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    model_source = _resolve_model_source()
    models_dir = Path(model_source).parent if isinstance(model_source, Path) else Path("./models")
    cv = CVService(models_dir=models_dir, model_source=model_source)

    if reset:
        request.app.state.db.reset_detections()

    results = cv.detect_directory(static_dir, confidence=confidence, limit=limit)
    saved = []

    for img_path, detections in results.items():
        ts = datetime.fromtimestamp(img_path.stat().st_mtime)
        for d in detections:
            det_data = {
                "timestamp": ts,
                "imagem_nome": img_path.name,
                "classe": d.class_name,
                "confianca": d.confidence,
                "bbox": str(d.bbox),
            }
            try:
                request.app.state.db.create_detection(det_data)
                saved.append(det_data)
            except Exception as e:
                logger.warning("save_detection_failed", error=str(e), image=img_path.name)

    return {
        "images_processed": len(results),
        "detections_saved": len(saved),
        "classes": sorted({d['classe'] for d in saved}) if saved else [],
        "static_dir": str(static_dir),
        "model_source": str(model_source),
    }


@router.get("/history")
async def get_history(request: Request, limit: int = 20):
    try:
        detections = request.app.state.db.get_detections(limit=limit)
        return [
            {
                "timestamp": d.timestamp.strftime("%Y-%m-%d %H:%M"),
                "image": d.imagem_nome,
                "classe": d.classe,
                "objects": 1,
                "confidence": float(d.confianca) * 100,
            }
            for d in detections
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
