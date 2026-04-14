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
            entrada = input("Introduce la temperatura (-20 a 50 °C) [o 'c' para cancelar]: ").strip()
            if entrada.lower() == 'c': raise KeyboardInterrupt # Simula la cancelación
            
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
            entrada = input("Introduce la humedad (0 a 100%) [o 'c' para cancelar]: ").strip()
            if entrada.lower() == 'c': raise KeyboardInterrupt
            
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
            entrada = input("Introduce la velocidad del viento (0 a 150 km/h) [o 'c' para cancelar]: ").strip()
            if entrada.lower() == 'c': raise KeyboardInterrupt
            
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
    Solo permite fechas actuales o pasadas (no futuras).
    """
    while True:
        entrada = input("Introduce la fecha (formato AAAA-MM-DD, ej: 2026-04-06) [o 'c' para cancelar]: ").strip()
        if entrada.lower() == 'c': raise KeyboardInterrupt

        if not entrada:
            print("❌ Error: La fecha no puede estar vacía.")
            continue

        try:
            # Comprueba si la fecha existe en el calendario real
            fecha_ingresada = datetime.strptime(entrada, "%Y-%m-%d")
            fecha_actual = datetime.now()

            # Valida que no sea una fecha futura
            if fecha_ingresada > fecha_actual:
                print(f"❌ Error: No se permiten fechas futuras. La fecha ingresada ({entrada}) es posterior a hoy ({fecha_actual.strftime('%Y-%m-%d')}).")
                print("🔄 Inténtalo de nuevo.\n")
                continue

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
        zona_input = input("Introduce la zona (ej: Retiro, Centro) [o 'c' para cancelar]: ").strip()
        if zona_input.lower() == 'c': raise KeyboardInterrupt
        
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
        
def validar_acceso():
    """
    Valida que el empleado exista en empleados.json.
    Devuelve el número de empleado si es válido, None si no.
    PARA REGISTRO DE NUEVO USUARIO.

    USO:
    - auth.py (registrar_usuario): num_empleado = validar_acceso()
    """
    max_intentos = 3
    intento = 0

    try:
        with open("empleados.json", "r", encoding='utf-8') as f:
            lista_autorizados = json.load(f)
    except FileNotFoundError:
        print("❌ Error crítico: El archivo 'empleados.json' no existe.")
        return None
    except json.JSONDecodeError:
        print("❌ Error crítico: El archivo 'empleados.json' está corrupto.")
        return None

    while intento < max_intentos:
        try:
            numero_ingresado = input(f"Introduce tu número de empleado [{intento + 1}/{max_intentos}] [o 'c' para cancelar]: ").strip()

            if numero_ingresado.lower() == 'c':
                raise KeyboardInterrupt

            if not numero_ingresado:
                print("❌ Error: El número de empleado no puede estar vacío.")
                intento += 1
                continue

            # Búsqueda exacta en la lista
            if numero_ingresado in lista_autorizados:
                print(f"✅ Número de empleado {numero_ingresado} validado correctamente.")
                return numero_ingresado  # Devolvemos el número válido
            else:
                intento += 1
                intentos_restantes = max_intentos - intento
                print(f"❌ Número de empleado NO reconocido.")
                if intentos_restantes > 0:
                    print(f"🔄 Intentos restantes: {intentos_restantes}\n")
                else:
                    print(f"❌ Has agotado los {max_intentos} intentos.\n")
                    
        except KeyboardInterrupt:
            print("❌ Validación cancelada por el usuario.")
            return None
    
    return None  # Si agota intentos, devuelve None


def validar_duplicado(nueva_fecha, nueva_zona, historial):
    """
    Comprueba si ya existe un registro para la misma fecha y zona.
    
    DEV 3 / DEV 1: Pasad a esta función la fecha, la zona y el JSON cargado.
    Retorna: True (si hay error de duplicado) o False (si todo está correcto).
    """
    for registro in historial:
        if registro['fecha'] == nueva_fecha and registro['distrito'].lower() == nueva_zona.lower():
            print(f"❌ Error: Ya existen datos para '{nueva_zona}' en la fecha {nueva_fecha}.")
            print("⚠️ No se permiten registros duplicados para la misma zona el mismo día.")
            return True 
            
    return False


def validar_usuario_sesion():
    """
    Valida que el usuario exista en usuarios.json.
    Devuelve el número de empleado si es válido, None si no.
    PARA INICIAR SESIÓN SOLAMENTE.

    USO:
    - auth.py (iniciar_sesion): num_empleado = validar_usuario_sesion()
    """
    max_intentos = 3
    intento = 0

    try:
        with open("usuarios.json", "r", encoding='utf-8') as f:
            usuarios_registrados = json.load(f)
            numeros_usuarios = [u.get("num_empleado") for u in usuarios_registrados]
    except FileNotFoundError:
        print("❌ Error crítico: El archivo 'usuarios.json' no existe.")
        return None
    except json.JSONDecodeError:
        print("❌ Error crítico: El archivo 'usuarios.json' está corrupto.")
        return None

    while intento < max_intentos:
        try:
            numero_ingresado = input(f"Introduce tu número de empleado [{intento + 1}/{max_intentos}] [o 'c' para cancelar]: ").strip()

            if numero_ingresado.lower() == 'c':
                raise KeyboardInterrupt

            if not numero_ingresado:
                print("❌ Error: El número de empleado no puede estar vacío.")
                intento += 1
                continue

            # Búsqueda exacta en usuarios registrados
            if numero_ingresado in numeros_usuarios:
                print(f"✅ Usuario {numero_ingresado} encontrado.")
                return numero_ingresado
            else:
                intento += 1
                intentos_restantes = max_intentos - intento
                if intentos_restantes > 0:
                    print(f"❌ Este usuario no está registrado. Intentos restantes: {intentos_restantes}")
                else:
                    print("❌ Has agotado los intentos.")
        except KeyboardInterrupt:
            raise

    return None

def validar_lluvia():
    """
    Solicita y valida la cantidad de lluvia (precipitaciones).
    Rango permitido: 0 a 500 mm.
    
    DEV 1 / DEV 2: Llama a esta función sin parámetros.
    Retorna: Un número float (ej. 15.5).
    """
    while True:
        try:
            entrada = input("Introduce la cantidad de lluvia (0 a 500 mm) [o 'c' para cancelar]: ").strip()
            if entrada.lower() == 'c': raise KeyboardInterrupt
            
            lluvia = float(entrada)
            
            # La lluvia no puede ser negativa, y ponemos un tope lógico de 500mm
            if 0 <= lluvia <= 500:
                return lluvia  
            else:
                print(f"❌ Error: {lluvia} mm está fuera del rango lógico (0 a 500).")
        
        except ValueError:
            print("❌ Error: La cantidad de lluvia debe ser un valor numérico (ejemplo: 12.5).")
            
        print("🔄 Inténtalo de nuevo.\n")