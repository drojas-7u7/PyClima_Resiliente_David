import json
import os
import getpass # librería nativa que hace que se oculte el texto; es un método de seguridad para la contraseña

ARCHIVO_USUARIOS = 'usuarios.json'
ARCHIVO_CLIMA = 'datos_clima.json'

def cargar_datos(archivo):
    if not os.path.exists(archivo): return []
    try:
        with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def guardar_datos(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def imprimir_detalle(r, idx=None):
    id_txt = f"ID: {idx} | " if idx is not None else ""
    edit_txt = " [EDITADO]" if r.get("editado") else ""
    alertas = ", ".join(r.get("alertas", [])) if r.get("alertas") else "Ninguna"
    print(f"{id_txt}Fecha: {r['fecha']} | Distrito: {r['distrito']} | Zona: {r.get('zona', 'N/A')}")
    print(f"      Temp: {r['temp']}°C | Hum: {r['humedad']}% | Viento: {r['viento']}km/h")
    print(f"      Lluvia: {r['lluvia']}mm | Alertas: {alertas}{edit_txt}")
    print("-" * 75)

def registrar_usuario():
    print("\n--- REGISTRO ---")
    nombre = input("Nombre: ")
    apellidos = input("Apellidos: ")
    while True:
        num = input("Número empleado (6 dígitos): ")
        if num.isdigit() and len(num) == 6: break
        print("Error: Deben ser 6 números.")
    while True:
        # Reemplazamos input() por getpass.getpass() para que no se muestra la contraseña
        pw = getpass.getpass("Contraseña (8+ alfanuméricos): ")
        if len(pw) >= 8 and pw.isalnum(): break
        print("Error: Mínimo 8 caracteres sin símbolos.")
    
    usuarios = cargar_datos(ARCHIVO_USUARIOS)
    usuarios.append({"nombre": nombre, "apellidos": apellidos, "num_empleado": num, "password": pw})
    guardar_datos(ARCHIVO_USUARIOS, usuarios)
    print("Registro exitoso.")

def iniciar_sesion():
    num = input("Número empleado: ")
    # Reemplazamos input() por getpass.getpass()
    pw = getpass.getpass("Contraseña: ")
    for u in cargar_datos(ARCHIVO_USUARIOS):
        if u["num_empleado"] == num and u["password"] == pw:
            print(f"\n✅ Bienvenido/a, {u['nombre']} {u['apellidos']} (ID Operario: {u['num_empleado']})")
            return u
    print("Datos incorrectos.")
    return None

def consultar_y_editar_historial(num_empleado):
    registros = cargar_datos(ARCHIVO_CLIMA)
    mis_indices = [i for i, r in enumerate(registros) if r.get("registrado_por") == num_empleado]

    if not mis_indices:
        print("No tienes registros.")
        return

    for i in mis_indices: imprimir_detalle(registros[i], i)

    opcion = input("\n¿ID del registro que deseas corregir por completo? (Enter para salir): ").strip()
    
    if opcion.isdigit() and int(opcion) in mis_indices:
        idx = int(opcion)
        if registros[idx].get("editado"):
            print("ERROR: Este registro ya fue corregido anteriormente y está bloqueado.")
        else:
            print(f"\n Vas a editar TODO el registro de {registros[idx]['distrito']} del día {registros[idx]['fecha']}.")
            confirmar = input("¿Estás seguro de que quieres continuar? Solo podrás hacerlo UNA VEZ (si/no): ").strip().lower()
            
            if confirmar == "si":
                try:
                    print("\n--- INTRODUCE LOS NUEVOS DATOS CORRECTOS ---")
                    
                    registros[idx]["distrito"] = input(f"Nuevo Distrito (actual: {registros[idx]['distrito']}): ").strip().title()
                    registros[idx]["temp"] = float(input(f"Nueva Temperatura (actual: {registros[idx]['temp']}): "))
                    registros[idx]["humedad"] = int(input(f"Nueva Humedad % (actual: {registros[idx]['humedad']}): "))
                    registros[idx]["viento"] = float(input(f"Nueva Vel. Viento km/h (actual: {registros[idx]['viento']}): "))
                    registros[idx]["lluvia"] = float(input(f"Nueva Lluvia mm (actual: {registros[idx]['lluvia']}): "))
                    registros[idx]["editado"] = True 
                    
                    guardar_datos(ARCHIVO_CLIMA, registros)
                    print("\nRegistro corregido y guardado con éxito.")
                    
                except ValueError:
                    print("Error: Has introducido un formato de número incorrecto. No se guardaron los cambios.")
            else:
                print("Operación cancelada.")

def consultar_por_distrito():
    distrito = input("Distrito: ").strip().title()
    for r in cargar_datos(ARCHIVO_CLIMA):
        if r.get("distrito") == distrito: imprimir_detalle(r)

def consultar_por_fecha():
    fecha = input("Fecha (YYYY-MM-DD): ")
    for r in cargar_datos(ARCHIVO_CLIMA):
        if r.get("fecha") == fecha: imprimir_detalle(r)

def obtener_nombre_operario(num_empleado):
    """
    Traductor de identidades: Recibe un número de empleado y 
    devuelve un texto formateado con su nombre, apellido y número.
    """
    if not num_empleado or num_empleado == "Desconocido":
        return "Operario Desconocido"
        
    usuarios = cargar_datos(ARCHIVO_USUARIOS)
    
    for u in usuarios:
        if u["num_empleado"] == num_empleado:
            return f"👤 {u['nombre']} {u['apellidos']} (ID: {num_empleado})"
            
    return f"👤 Usuario no registrado (ID: {num_empleado})"