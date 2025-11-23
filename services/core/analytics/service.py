"""Analytics Service - Statistical analysis and reporting"""
import pandas as pd
import numpy as np
from typing import Dict, List
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import structlog

logger = structlog.get_logger()

class AnalyticsService:
    """Provides statistical analysis and reporting"""
    
    def calculate_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate descriptive statistics"""
        try:
            stats = {
                "mean": data.mean().to_dict(),
                "median": data.median().to_dict(),
                "std": data.std().to_dict(),
                "min": data.min().to_dict(),
                "max": data.max().to_dict(),
                "quartiles": data.quantile([0.25, 0.5, 0.75]).to_dict()
            }
            logger.info("statistics_calculated", columns=len(data.columns))
            return stats
        except Exception as e:
            logger.error("statistics_calculation_failed", error=str(e))
            return {}
    
    def calculate_correlations(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix"""
        return data.corr()
    
    def detect_anomalies(self, data: pd.DataFrame, threshold: float = 3.0) -> List[int]:
        """Detect anomalies using Z-score"""
        z_scores = np.abs((data - data.mean()) / data.std())
        anomalies = (z_scores > threshold).any(axis=1)
        return data[anomalies].index.tolist()
    
    def calculate_costs(self, readings: List, config: Dict) -> Dict:
        """Calculate operational costs"""
        total_activations = sum(1 for r in readings if r.bomba_ligada)
        water_cost = total_activations * config.get("water_cost_per_cycle", 0.5)
        energy_cost = total_activations * config.get("energy_cost_per_cycle", 0.3)
        return {"water_cost": water_cost, "energy_cost": energy_cost, "total": water_cost + energy_cost}
    
    def generate_pdf_report(self, data: Dict, output_path: Path) -> Path:
        """Generate PDF report"""
        c = canvas.Canvas(str(output_path), pagesize=letter)
        c.drawString(100, 750, "FarmTech Analytics Report")
        c.drawString(100, 730, f"Generated: {pd.Timestamp.now()}")
        c.save()
        logger.info("pdf_report_generated", path=str(output_path))
        return output_path
    
    def run_r_analysis(self, data: dict) -> dict:
        """Run R analysis script with robust error handling"""
        import subprocess
        import json
        import tempfile
        import os
        
        try:
            r_script_path = Path(__file__).parent / "analysis.R"
            
            # Validate input data
            if not data or not isinstance(data, dict):
                raise ValueError("Input data must be a non-empty dictionary")
            
            # Create temp file with data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f)
                temp_file = f.name
            
            try:
                # Check if R script exists
                if not r_script_path.exists():
                    logger.error("r_script_not_found", path=str(r_script_path))
                    raise FileNotFoundError(f"R script not found at {r_script_path}")
                
                # Run R script with timeout
                result = subprocess.run(
                    ['Rscript', str(r_script_path), temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Check for errors
                if result.returncode != 0:
                    logger.error("r_script_failed", stderr=result.stderr, returncode=result.returncode)
                    raise RuntimeError(f"R script failed: {result.stderr}")
                
                # Parse output
                try:
                    output = json.loads(result.stdout)
                except json.JSONDecodeError as e:
                    logger.error("r_output_parse_failed", stdout=result.stdout, error=str(e))
                    raise ValueError(f"Failed to parse R output as JSON: {result.stdout}")
                
                logger.info("r_analysis_success", output=output)
                return output
                
            except FileNotFoundError as e:
                logger.error("rscript_not_found", error=str(e))
                raise RuntimeError("Rscript not found. Install R from https://www.r-project.org/")
            except subprocess.TimeoutExpired:
                logger.error("r_script_timeout")
                raise TimeoutError("R script execution exceeded 30 seconds")
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
            
        except Exception as e:
            logger.error("r_analysis_error", error=str(e), error_type=type(e).__name__)
            raise
