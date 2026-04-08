"""
Módulo de Lógica de Negocio - PyClima Resiliente
Responsable: DEV 1 (Lógica Principal)
Descripción: Orquestación de validaciones, preparación de estructuras de datos 
             y cálculo de métricas climáticas.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

# Importaciones de módulos de colaboradores
import persistencia  # DEV 3
import alertas       # DEV 4 (Lógica de alertas)
from validaciones import (
    validar_zona, 
    validar_input_numerico
) # DEV 2

class LogicaClima:
    def __init__(self):
        self.umbrales = persistencia.obtener_umbrales_alerta()

    def preparar_registro_climatico(
        self, 
        fecha: str, 
        distrito: str, 
        temp: float, 
        humedad: float, 
        viento: float, 
        lluvia: bool, 
        usuario_id: str
    ) -> Dict[str, Any]:
        """
        Estructura el diccionario oficial del proyecto.
        """
        # Delegamos el cálculo de alertas al módulo de alertas (DEV 4)
        lista_alertas = alertas.evaluar_alertas(
            temp, viento, humedad, self.umbrales
        )

        return {
            "fecha": fecha,
            "distrito": distrito,
            "temp": temp,
            "humedad": humedad,
            "viento": viento,
            "lluvia": lluvia,
            "alertas": lista_alertas,
            "registrado_por": usuario_id,
            "editado": False,
            "timestamp_servidor": datetime.now().isoformat()
        }

    def verificar_duplicado(self, fecha: str, distrito: str) -> bool:
        """
        Comprueba si ya existe un registro para ese distrito en esa fecha.
        """
        historico = persistencia.leer_historico()
        for registro in historico:
            if registro.get("fecha") == fecha and registro.get("distrito") == distrito:
                return True
        return False

    def procesar_flujo_registro(self, datos_raw: Dict[str, Any]) -> bool:
        """
        Orquestador Principal: Valida, Verifica, Estructura y Guarda.
        Lanza excepciones si algo falla para que la Interfaz las capture.
        """
        # 1. Validaciones de Dominio (Delegadas a DEV 2)
        distrito_validado = validar_zona(datos_raw["distrito"])
        
        # 2. Verificación de Reglas de Negocio (Duplicados)
        if self.verificar_duplicado(datos_raw["fecha"], distrito_validado):
            raise ValueError(f"Ya existe un registro para {distrito_validado} en la fecha {datos_raw['fecha']}.")

        # 3. Preparación del objeto final
        registro_final = self.preparar_registro_climatico(
            fecha=datos_raw["fecha"],
            distrito=distrito_validado,
            temp=datos_raw["temp"],
            humedad=datos_raw["humedad"],
            viento=datos_raw["viento"],
            lluvia=datos_raw["lluvia"],
            usuario_id=datos_raw["usuario_id"]
        )

        # 4. Persistencia (Delegada a DEV 3)
        exito = persistencia.registrar_nuevo_dato(registro_final)
        return exito

    def calcular_metricas_distrito(self, nombre_distrito: str) -> Dict[str, Any]:
        """
        Calcula promedios y máximos para el Ayuntamiento.
        """
        historico = persistencia.leer_historico()
        datos_zona = [r for r in historico if r["distrito"].lower() == nombre_distrito.lower()]

        if not datos_zona:
            return {}

        temps = [r["temp"] for r in datos_zona]
        vientos = [r["viento"] for r in datos_zona]

        return {
            "promedio_temp": round(sum(temps) / len(temps), 2),
            "max_temp": max(temps),
            "max_viento": max(vientos),
            "total_registros": len(datos_zona)
        }