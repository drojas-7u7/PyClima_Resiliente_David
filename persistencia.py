import json
import os

ARCHIVO_JSON = "datos_clima.json" #LLamada a los archivos y definirlos
CONFIGURACIÓN_DE_ARCHIVO = "config.json"
CONFIRMACIÓN_REQUERIDA = "si"

def obtener_distritos_permitidos():    #Función para obtener la lista de distritos oficiales desde el archivo de configuración
    if not os.path.exists(CONFIGURACIÓN_DE_ARCHIVO):
        print(f"❌ Alerta: No se encontró {CONFIGURACIÓN_DE_ARCHIVO}. Se desactivó la validación territorial. ❌")
        return []
    try:
        with open(CONFIGURACIÓN_DE_ARCHIVO, 'r', encoding='utf-8') as F:
            configuración = json.load(F)
            return configuración.get("distritos_oficiales", [])
    except Exception:
        return []
    
def obtener_umbrales_alerta():  #Función para obtener los umbrales de alerta desde el archivo de configuración
    if not os.path.exists(CONFIGURACIÓN_DE_ARCHIVO):
        print(f"❌ Alerta: No se encontró {CONFIGURACIÓN_DE_ARCHIVO}. Sistema sin umbrales. ❌")
        return {}

    try:
        with open(CONFIGURACIÓN_DE_ARCHIVO, 'r', encoding='utf-8') as F:
            configuración = json.load(F)
            umbrales = configuración.get("umbrales", {})
            return umbrales
    except Exception:
        print(f"❌ Error al leer umbrales de {CONFIGURACIÓN_DE_ARCHIVO}. ❌")
        return {}

def leer_historico():    #Función para leer el histórico de datos desde el archivo JSON, con manejo de errores
    if not os.path.exists(ARCHIVO_JSON):
        print(f"❌ Alerta: No se encontró {ARCHIVO_JSON}. ❌")
        return []
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as F:
            return json.load(F)
    except json.JSONDecodeError:
        print("❌ Error: El archivo de datos está corrupto ❌")
        return []
    except Exception as error:
        print(f"❌ Error: No se pudo leer el archivo de datos: {error} ❌")
        return []

def registrar_nuevo_dato(nuevo_registro):  #Función para registrar un nuevo dato, con validación de distrito, verificación de duplicados y confirmación del usuario
    distritos_oficiales = obtener_distritos_permitidos()
    distrito_ingresado = nuevo_registro["distrito"].strip()
    mapa_distritos = {distrito.lower(): distrito for distrito in distritos_oficiales}
    distrito_limpio = mapa_distritos.get(distrito_ingresado.lower(), distrito_ingresado)

    if distritos_oficiales and distrito_limpio not in distritos_oficiales:
        print(f"❌ Error: '{distrito_limpio}' no es un distrito oficial de Madrid. ❌")
        return False

    historico = leer_historico()
    for entrada in historico:
        if entrada["fecha"] == nuevo_registro["fecha"]:
            if entrada["distrito"].lower() == distrito_limpio.lower():
                print(f"❌ ERROR: Ya existe un registro para {distrito_limpio} en la fecha {nuevo_registro['fecha']} ❌")
                print("❌ No se permiten duplicados en el histórico. ❌")
                return False

    print(f"\nDatos a registrar: {distrito_limpio} | {nuevo_registro['fecha']} | {nuevo_registro['temperatura']}°C")
    
    # --- PASO 2: BUCLE DE CONFIRMACIÓN ---
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
                print(f"❌ Error crítico al escribir en el disco: {mi} ❌")
                return False
                
        elif confirmar == 'n':
            print("❌ Operación cancelada. No se han guardado los datos ❌")
            return False
            
        else:
            print("⚠️ No te he entendido. Por favor, escribe únicamente 's' para Sí o 'n' para No ⚠️\n")

def actualizar_base_de_datos(historico_modificado):  #Función para actualizar la base de datos con un histórico modificado, con manejo de errores
    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
            json.dump(historico_modificado, F, indent=4, ensure_ascii=False)
        return True
    except Exception as mi:
        print(f"❌ Error al actualizar la base de datos: {mi} ❌")
        return False

def inicializar_archivo_datos():   #Función para inicializar el archivo de datos si no existe, con manejo de errores
    if not os.path.exists(ARCHIVO_JSON):
        print(f"⚙️  Inicializando sistema: Creando nueva base de datos ({ARCHIVO_JSON})...")
        try:
            with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
                json.dump([], f)
        except Exception as e:
            print(f"❌ Error crítico al crear la base de datos: {e} ❌")
