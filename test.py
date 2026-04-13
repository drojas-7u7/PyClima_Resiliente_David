import logging
import os
import pytest
from alertas import evaluar_alertas
from validaciones import validar_temperatura, validar_viento


if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/trazabilidad_tests.log", encoding="utf-8")],
)
logger = logging.getLogger(__name__)


@pytest.fixture
def umbrales():
    return {
        "temp_max_naranja": 35.0,
        "temp_max_roja": 40.0,
        "temp_min_alerta": 2.0,
        "temp_min_emergencia": -2.0,
        "temp_min_critica": -5.0,
        "viento_max": 40,
        "lluvia_naranja": 20.0,
        "lluvia_roja": 50.0,
        "humedad_min": 15,
    }


def test_validar_viento_rango_logico(monkeypatch):
    logger.info("Iniciando test: Validacion de viento (Rango logico)")
    monkeypatch.setattr("builtins.input", lambda _: "25.5")

    resultado = validar_viento()

    assert resultado == 25.5
    logger.info("Resultado: El sistema acepto 25.5 km/h correctamente.")


def test_validar_temperatura_rango_logico(monkeypatch):
    logger.info("Iniciando test: Validacion de temperatura (Rango logico)")
    monkeypatch.setattr("builtins.input", lambda _: "22.5")

    resultado = validar_temperatura()

    assert resultado == 22.5
    logger.info("Resultado: El sistema acepto 22.5 C correctamente.")


def test_alerta_peligro_viento(umbrales):
    logger.info("Iniciando test: Deteccion automatica de peligro (Viento)")
    datos = {"temperatura": 20, "viento": 60, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert any("VIENTO" in alerta.upper() for alerta in alertas)
    logger.info("Resultado: Alerta generada con exito.")


def test_calor_extremo_activa_alerta_roja(umbrales):
    logger.info("Iniciando test: Calor extremo activa alerta roja")
    datos = {"temperatura": 41, "viento": 0, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 1
    assert any("Alerta Roja" in alerta and "Calor extremo" in alerta for alerta in alertas)
    logger.info("Resultado: Alerta roja de calor extremo generada.")


def test_helada_emergencia_a_menos_tres_grados(umbrales):
    logger.info("Iniciando test: Helada emergencia")
    datos = {"temperatura": -3, "viento": 0, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 1
    assert any("HELADA" in alerta and "Riesgo infraestructuras" in alerta for alerta in alertas)
    logger.info("Resultado: Alerta de helada emergencia generada.")


def test_lluvia_torrencial_activa_alerta_roja(umbrales):
    logger.info("Iniciando test: Lluvia torrencial")
    datos = {"temperatura": 20, "viento": 0, "humedad": 50, "lluvia": 60}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 1
    assert any("LLUVIA" in alerta and "Alerta Roja" in alerta for alerta in alertas)
    logger.info("Resultado: Alerta roja de lluvia torrencial generada.")


def test_situacion_normal_no_dispara_alertas(umbrales):
    logger.info("Iniciando test: Situacion normal sin alertas")
    datos = {"temperatura": 20, "viento": 0, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert alertas == []
    logger.info("Resultado: No se generaron alertas.")


def test_calor_y_viento_fuerte_generan_alertas_combinadas(umbrales):
    logger.info("Iniciando test: Alertas combinadas (calor y viento)")
    datos = {"temperatura": 41, "viento": 55, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 2
    assert any("Calor extremo" in alerta for alerta in alertas)
    assert any("VIENTO" in alerta for alerta in alertas)
    logger.info("Resultado: Se generaron 2 alertas combinadas.")


def test_temperatura_exacta_de_cuarenta_activa_roja_y_no_naranja(umbrales):
    logger.info("Iniciando test: Temperatura en umbral rojo")
    datos = {"temperatura": 40, "viento": 0, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert any("Alerta Roja" in alerta for alerta in alertas)
    assert not any("Alerta Naranja" in alerta and "Temperatura elevada" in alerta for alerta in alertas)
    logger.info("Resultado: Alerta roja correcta en umbral.")


def test_lluvia_intensa_en_umbral_naranja(umbrales):
    logger.info("Iniciando test: Lluvia intensa en umbral naranja")
    datos = {"temperatura": 18, "viento": 0, "humedad": 50, "lluvia": 20}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 1
    assert any("Lluvia intensa" in alerta for alerta in alertas)
    assert any("Alerta Naranja" in alerta for alerta in alertas)
    logger.info("Resultado: Alerta naranja de lluvia intensa generada.")


def test_humedad_muy_baja_activa_alerta_de_sequedad(umbrales):
    logger.info("Iniciando test: Humedad muy baja (sequedad)")
    datos = {"temperatura": 25, "viento": 0, "humedad": 10, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 1
    assert any("SEQUEDAD" in alerta for alerta in alertas)
    logger.info("Resultado: Alerta de sequedad generada.")


def test_helada_preventiva_en_umbral_de_alerta(umbrales):
    logger.info("Iniciando test: Helada preventiva")
    datos = {"temperatura": 2, "viento": 0, "humedad": 50, "lluvia": 0}

    alertas = evaluar_alertas(datos, umbrales)

    assert len(alertas) == 1
    assert any("helada preventiva" in alerta.lower() for alerta in alertas)
    logger.info("Resultado: Alerta de helada preventiva generada.")


def test_acepta_valores_como_cadenas_numericas(umbrales):
    logger.info("Iniciando test: Valores como cadenas numericas")
    datos = {"temperatura": "41", "viento": "40", "humedad": "15", "lluvia": "50"}

    alertas = evaluar_alertas(datos, umbrales)

    assert any("Calor extremo" in alerta for alerta in alertas)
    assert any("VIENTO" in alerta for alerta in alertas)
    assert any("LLUVIA" in alerta for alerta in alertas)
    assert any("SEQUEDAD" in alerta for alerta in alertas)
    logger.info("Resultado: Todas las alertas se generaron correctamente.")
