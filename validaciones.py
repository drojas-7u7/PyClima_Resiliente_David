"""
MÓDULO DE VALIDACIONES (DEV 2 - David)
--------------------------------------
Este módulo contiene todas las reglas de calidad de datos del Ayuntamiento.
Proporciona funciones seguras que no rompen el programa si el usuario se equivoca.

Instrucciones para el equipo:
- DEV 1: Importa estas funciones en tu menu.py (ej: from validaciones import validar_temperatura)
- DEV 3: Usa validar_duplicado antes de guardar en tu archivo JSON.
"""

from datetime import datetime
import json
import difflib

def validar_temperatura():
    """
    Solicita y valida la temperatura.
    Rango permitido: -20 a 50 grados Celsius.
    
    DEV 1: Llama a esta función sin parámetros.
    Retorna: Un número float (ej. 25.5).
    """
    while True:
        try:
            entrada = input("Introduce la temperatura (-20 a 50 °C): ")
            temp = float(entrada)
            
            if -20 <= temp <= 50:
                return temp  
            else:
                print(f"❌ Error: {temp}°C está fuera del rango permitido (-20 a 50).")
        
        except ValueError:
            print("❌ Error: Por favor, introduce un número válido (ejemplo: 25.5).")
        
        print("🔄 Inténtalo de nuevo.\n")


def validar_humedad():
    """
    Solicita y valida la humedad ambiental.
    Rango permitido: 0 a 100%.
    
    DEV 1: Llama a esta función sin parámetros.
    Retorna: Un número float (ej. 45.0).
    """
    while True:
        try:
            entrada = input("Introduce la humedad (0 a 100%): ")
            humedad = float(entrada)
            
            if 0 <= humedad <= 100:
                return humedad  
            else:
                print(f"❌ Error: {humedad}% no es una humedad lógica (debe ser de 0 a 100).")
        
        except ValueError:
            print("❌ Error: Introduce un valor numérico para la humedad.")
            
        print("🔄 Inténtalo de nuevo.\n")


def validar_viento():
    """
    Solicita y valida la velocidad del viento.
    Rango permitido: 0 a 150 km/h.
    
    DEV 1: Llama a esta función sin parámetros.
    Retorna: Un número float (ej. 12.5).
    """
    while True:
        try:
            entrada = input("Introduce la velocidad del viento (0 a 150 km/h): ")
            viento = float(entrada)
            
            if 0 <= viento <= 150:
                return viento  
            else:
                print(f"❌ Error: {viento} km/h está fuera del rango lógico (0 a 150).")
        
        except ValueError:
            print("❌ Error: La velocidad del viento debe ser un valor numérico.")
            
        print("🔄 Inténtalo de nuevo.\n")


def validar_fecha():
    """
    Solicita y valida una fecha.
    Formato estricto: AAAA-MM-DD.
    
    DEV 1: Llama a esta función sin parámetros.
    Retorna: Un string con la fecha correcta (ej. '2026-04-06').
    """
    while True:
        entrada = input("Introduce la fecha (formato AAAA-MM-DD, ej: 2026-04-06): ").strip()
        
        if not entrada:
            print("❌ Error: La fecha no puede estar vacía.")
            continue 
            
        try:
            # Comprueba matemáticamente si la fecha existe en el calendario real
            datetime.strptime(entrada, "%Y-%m-%d")
            return entrada
            
        except ValueError:
            print("❌ Error: Formato incorrecto o fecha inexistente. Usa AAAA-MM-DD.")
            
        print("🔄 Inténtalo de nuevo.\n")


def validar_zona():
    """
    Solicita el nombre de la zona y lo coteja con config.json.
    - No distingue mayúsculas/minúsculas.
    - Devuelve el nombre exacto oficial (ej. si escribes 'retiro', devuelve 'Retiro').
    - Sugiere el nombre si hay un error tipográfico.
    """
    # 1. Cargar el archivo de configuración (Sugerencia de Robustez)
    try:
        with open('config.json', 'r', encoding='utf-8') as archivo:
            config = json.load(archivo)
            distritos_oficiales = config.get("distritos_oficiales", [])
    except FileNotFoundError:
        print("❌ Error crítico: No se encuentra el archivo 'config.json'.")
        print("⚠️ Avisa al equipo técnico para restaurar el archivo.")
        return None 
    except json.JSONDecodeError:
        print("❌ Error crítico: El archivo 'config.json' está corrupto.")
        return None

    # Creamos un "diccionario traductor" para buscar en minúsculas pero recuperar la versión original
    mapa_distritos = {distrito.lower(): distrito for distrito in distritos_oficiales}
    lista_minusculas = list(mapa_distritos.keys())

    while True:
        # 2. Pedimos el dato y comprobamos que no esté vacío
        zona_input = input("Introduce la zona (ej: Retiro, Centro): ").strip()
        
        if not zona_input:
            print("❌ Error: La zona no puede estar vacía.")
            print("🔄 Inténtalo de nuevo.\n")
            continue

        zona_lower = zona_input.lower()

        # 3. Comprobación exacta (ignorando mayúsculas)
        if zona_lower in mapa_distritos:
            return mapa_distritos[zona_lower] # Devuelve el nombre oficial exacto

        # 4. Magia de corrección tipográfica (Sugerencias)
        # Busca coincidencias con al menos un 60% de similitud
        sugerencias = difflib.get_close_matches(zona_lower, lista_minusculas, n=1, cutoff=0.6)

        if sugerencias:
            # Si encuentra algo parecido, recuperamos el nombre oficial
            zona_sugerida = mapa_distritos[sugerencias[0]]
            confirmacion = input(f"🤔 No encuentro '{zona_input}'. ¿Querías decir '{zona_sugerida}'? (s/n): ").strip().lower()
            
            if confirmacion == 's':
                return zona_sugerida
            else:
                print("❌ Entendido. Zona descartada.")
        else:
            # Si lo que ha escrito no se parece a nada de Madrid
            print(f"❌ Error: '{zona_input}' no coincide con ningún distrito oficial de Madrid.")
            
        print("🔄 Inténtalo de nuevo.\n")


def validar_duplicado(nueva_fecha, nueva_zona, historial):
    """
    Comprueba si ya existe un registro para la misma fecha y zona.
    
    DEV 3 / DEV 1: Pasad a esta función la fecha, la zona y el JSON cargado.
    Retorna: True (si hay error de duplicado) o False (si todo está correcto).
    """
    for registro in historial:
        if registro['fecha'] == nueva_fecha and registro['zona'].lower() == nueva_zona.lower():
            print(f"❌ Error: Ya existen datos para '{nueva_zona}' en la fecha {nueva_fecha}.")
            print("⚠️ No se permiten registros duplicados para la misma zona el mismo día.")
            return True 
            
    return False