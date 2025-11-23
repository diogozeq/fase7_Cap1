"""CPTEC/INPE Weather API Client - Fase 1"""
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List
import structlog

logger = structlog.get_logger()

class CPTECClient:
    """Client for CPTEC/INPE Weather API"""
    
    def __init__(self, api_url: str = "http://servicos.cptec.inpe.br/XML/cidade/241/previsao.xml"):
        self.api_url = api_url
    
    def get_weather_data(self) -> Dict:
        """Fetch weather data from CPTEC API"""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            city = root.find('.//nome').text if root.find('.//nome') is not None else "Unknown"
            state = root.find('.//uf').text if root.find('.//uf') is not None else "Unknown"
            
            forecasts = []
            for previsao in root.findall('.//previsao'):
                forecasts.append({
                    "dia": previsao.find('dia').text if previsao.find('dia') is not None else "",
                    "tempo": previsao.find('tempo').text if previsao.find('tempo') is not None else "",
                    "maxima": previsao.find('maxima').text if previsao.find('maxima') is not None else "",
                    "minima": previsao.find('minima').text if previsao.find('minima') is not None else ""
                })
            
            logger.info("weather_data_fetched", city=city, forecasts=len(forecasts))
            return {"city": city, "state": state, "forecasts": forecasts}
        except Exception as e:
            logger.error("weather_fetch_failed", error=str(e))
            return {"error": str(e)}
