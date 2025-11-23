"""
Script de inicialização da API FastAPI
"""
import sys
from pathlib import Path
import os

# Add project root to Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# Also add services directory
services_dir = project_root / "services"
if services_dir.exists():
    sys.path.insert(0, str(services_dir.parent))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(project_root)

# Import and run uvicorn
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("FarmTech API - Fase 7")
    print("=" * 60)
    print()
    print("Iniciando servidor...")
    print("API Docs: http://localhost:8000/docs")
    print("Redoc: http://localhost:8000/redoc")
    print("Teste AWS: http://localhost:8000/api/alerts/test")
    print()
    print("Pressione CTRL+C para parar")
    print("=" * 60)
    print()

    # Use the full module path since we're running from project root
    api_dir = project_root / "services" / "api"

    uvicorn.run(
        "services.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(api_dir)],
        log_level="info"
    )
