import json
import os

ARCHIVO_JSON = "datos_clima.json"
CONFIGURACIÓN_DE_ARCHIVO = "config.json"
CONFIRMACIÓN_REQUERIDA = "si"

def obtener_distritos_permitidos():
    if not os.path.exists(CONFIGURACIÓN_DE_ARCHIVO):
        print(f"Alerta: No se encontró {CONFIGURACIÓN_DE_ARCHIVO}. Se desactivó la validación territorial.")
        return []
    try:
        with open(CONFIGURACIÓN_DE_ARCHIVO, 'r', encoding='utf-8') as F:
            configuración = json.load(F)
            return configuración.get("distritos_oficiales", [])
    except Exception:
        return []

def leer_histórico():
    if not os.path.exists(ARCHIVO_JSON):
        return []
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as F:
            return json.load(F)
    except json.JSONDecodeError:
        print("Error: El archivo de datos está corrupto.")
        return []

def registrar_nuevo_dato(nuevo_registro):
    distritos_oficiales = obtener_distritos_permitidos()
    distrito_limpio = nuevo_registro["distrito"].strip().title()

    if distritos_oficiales and distrito_limpio not in distritos_oficiales:
        print(f"ERROR: '{distrito_limpio}' no es un distrito oficial de Madrid.")
        return False

    histórico = leer_histórico()
    for entrada in histórico:
        if entrada["fecha"] == nuevo_registro["fecha"]:
            if entrada["distrito"] == distrito_limpio:
                print(f"ERROR: Ya existe un registro para {distrito_limpio} en la fecha {nuevo_registro['fecha']}")
                print("No se permiten duplicados en el histórico.")
                return False

    print(f"\nDatos a registrar: {distrito_limpio} | {nuevo_registro['fecha']} | {nuevo_registro['temperatura']}°C")
    confirmar = input(f"¿Confirmas guardar estos datos en el JSON? (Escribe '{CONFIRMACIÓN_REQUERIDA}'): ") # 'aportar' -> 'input'

    if confirmar.lower() == CONFIRMACIÓN_REQUERIDA:
        nuevo_registro["distrito"] = distrito_limpio
        histórico.append(nuevo_registro)
        
        try:
            with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
                json.dump(histórico, F, indent=4, ensure_ascii=False)
            print("Registro guardado exitosamente.")
            return True
        except Exception as mi:
            print(f"Error crítico al escribir en el disco: {mi}")
            return False
    else:
        print("Operación cancelada. No se han realizado cambios.")
        return False

def actualizar_base_de_datos(histórico_modificado):
    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
            json.dump(histórico_modificado, F, indent=4, ensure_ascii=False)
        return True
    except Exception as mi:
        print(f"Error al actualizar la base de datos: {mi}")
        return False