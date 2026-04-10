import pytest
import logging
import os
from validaciones import validar_viento, validar_duplicado
from alertas import evaluar_alertas

if not os.path.exists('logs'): os.makedirs('logs')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("logs/trazabilidad_tests.log", encoding='utf-8')]
)
logger = logging.getLogger(__name__)

def test_validar_viento_rango_logico(monkeypatch):
    logger.info("Iniciando test: Validación de viento (Rango lógico)")
    monkeypatch.setattr('builtins.input', lambda _: "25.5")
    resultado = validar_viento()
    
    assert resultado == 25.5
    logger.info(f"Resultado: El sistema aceptó 25.5 km/h correctamente.")

def test_evitar_duplicados():
    logger.info("Iniciando test: Calidad del dataset (Duplicados)")
    historial_mock = [{"fecha": "2026-04-10", "zona": "Retiro"}]
    
    existe = validar_duplicado("2026-04-10", "Retiro", historial_mock)
    
    assert existe is True
    logger.info("Resultado: Se evitó la degradación del dataset bloqueando el duplicado.")

def test_alerta_peligro_viento():
    logger.info("Iniciando test: Detección automática de peligro (Viento)")
    datos = {"temperatura": 20, "viento": 60, "humedad": 50}
    umbrales = {"viento_max": 40}
    
    alertas = evaluar_alertas(datos, umbrales)
    
    assert any("VIENTO" in alerta.upper() for alerta in alertas)
    logger.info(f"Resultado: Alerta generada con éxito: {alertas}")