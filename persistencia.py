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
    
def obtener_umbrales_alerta():
    if not os.path.exists(CONFIGURACIÓN_DE_ARCHIVO):
        return {"temp_max_naranja": 35.0, "temp_max_roja": 40.0, "viento_max": 40, "humedad_min": 15}
    
    try:
        with open(CONFIGURACIÓN_DE_ARCHIVO, 'r', encoding='utf-8') as F:
            configuración = json.load(F)
            return configuración.get("umbrales", {})
    except Exception:
        return {"temp_max_naranja": 35.0, "temp_max_roja": 40.0, "viento_max": 40, "humedad_min": 15}

def leer_historico():
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

    historico = leer_historico()
    for entrada in historico:
        if entrada["fecha"] == nuevo_registro["fecha"]:
            if entrada["distrito"] == distrito_limpio:
                print(f"ERROR: Ya existe un registro para {distrito_limpio} en la fecha {nuevo_registro['fecha']}")
                print("No se permiten duplicados en el histórico.")
                return False

    print(f"\nDatos a registrar: {distrito_limpio} | {nuevo_registro['fecha']} | {nuevo_registro['temperatura']}°C")
    
    # --- PASO 2: BUCLE DE CONFIRMACIÓN PROFESIONAL ---
    while True:
        confirmar = input("¿Confirmas guardar estos datos en el sistema? (s/n): ").strip().lower()
        
        if confirmar == 's':
            nuevo_registro["distrito"] = distrito_limpio
            historico.append(nuevo_registro)
            
            try:
                with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
                    json.dump(historico, F, indent=4, ensure_ascii=False)
                print("✅ Registro guardado exitosamente.")
                return True
            except Exception as mi:
                print(f"❌ Error crítico al escribir en el disco: {mi}")
                return False
                
        elif confirmar == 'n':
            print("❌ Operación cancelada. No se han guardado los datos.")
            return False
            
        else:
            print("⚠️ No te he entendido. Por favor, escribe únicamente 's' para Sí o 'n' para No.\n")

def actualizar_base_de_datos(historico_modificado):
    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
            json.dump(historico_modificado, F, indent=4, ensure_ascii=False)
        return True
    except Exception as mi:
        print(f"Error al actualizar la base de datos: {mi}")
        return False

def inicializar_archivo_datos():
    """Verifica si existe el JSON principal, si no, lo crea vacío."""
    if not os.path.exists(ARCHIVO_JSON):
        print(f"⚙️  Inicializando sistema: Creando nueva base de datos ({ARCHIVO_JSON})...")
        try:
            with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
                json.dump([], f)
        except Exception as e:
            print(f"❌ Error crítico al crear la base de datos: {e}")