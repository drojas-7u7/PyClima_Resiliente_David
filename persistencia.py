import json
import os

ARCHIVO_JSON = "datos_clima.json"
ARCHIVO_CONFIG = "config.json"
CONFIRMACION_REQUERIDA = "si"

def obtener_distritos_permitidos():
    if not os.path.exists(ARCHIVO_CONFIG):
        print(f"Alerta: No se encontró {ARCHIVO_CONFIG}. Se desactivó la validación territorial.")
        return []
    try:
        with open(ARCHIVO_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("distritos_oficiales", [])
    except Exception:
        return []

def leer_historico():
    if not os.path.exists(ARCHIVO_JSON):
        return []
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: El archivo de datos está corrupto.")
        return []

def registrar_nuevo_dato(nuevo_registro):
    distritos_oficiales = obtener_distritos_permitidos()
    distrito_limpio = nuevo_registro["distrito"].strip().title()

    if distritos_oficiales and distrito_limpio not in distritos_oficiales:
        print(f"ERROR: '{distrito_limpio}' no es un distrito oficial de Madrid.")
        return False

    historico = leer_historico()
    for entrada in historico:
        if (entrada["fecha"] == nuevo_registro["fecha"] and 
            entrada["distrito"] == distrito_limpio):
            print(f"ERROR: Ya existe un registro para {distrito_limpio} en la fecha {nuevo_registro['fecha']}.")
            print("No se permiten duplicados en el histórico.")
            return False

    print(f"\nDatos a registrar: {distrito_limpio} | {nuevo_registro['fecha']} | {nuevo_registro['temp']}°C")
    confirmar = input(f"¿Confirmas guardar estos datos en el JSON? (Escribe '{CONFIRMACION_REQUERIDA}'): ")
    
    if confirmar.lower() == CONFIRMACION_REQUERIDA:
        nuevo_registro["distrito"] = distrito_limpio
        historico.append(nuevo_registro)
        
        try:
            with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
            print("Registro guardado exitosamente.")
            return True
        except Exception as e:
            print(f"Error crítico al escribir en el disco: {e}")
            return False
    else:
        print("Operación cancelada. No se han realizado cambios.")
        return False