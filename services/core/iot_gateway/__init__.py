"""
IoT Gateway Service for FarmTech Consolidado
"""
from .service import IoTGatewayService
from .irrigation_logic import apply_irrigation_logic

__all__ = ['IoTGatewayService', 'apply_irrigation_logic']
