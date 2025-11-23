"""
Script to run the API with correct PYTHONPATH
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set environment variable as well
os.environ['PYTHONPATH'] = str(project_root)

# Now import and run the API
if __name__ == "__main__":
    from services.api.main import app
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
