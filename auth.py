import json
import os
import getpass
import validaciones

DB_EMPLEADOS = "empleados.json"
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
    print("\n--- 📝 REGISTRO DE NUEVO USUARIO ---")
    
    # PASO 1: VALIDAR QUE SEA EMPLEADO AUTORIZADO
    print("\n[PASO 1/3] Verificación de autenticidad del empleado")
    print("-" * 50)
    num_empleado = validaciones.validar_acceso()  # ← NUEVA VALIDACIÓN
    
    if num_empleado is None:
        print("❌ No se puede continuar sin un número de empleado válido.")
        return  # Cancela el registro
    
    # PASO 2: RECOPILAR DATOS PERSONALES
    print("\n[PASO 2/3] Información personal")
    print("-" * 50)
    nombre = input("Nombre: ").strip()
    apellidos = input("Apellidos: ").strip()
    
    # PASO 3: ESTABLECER CONTRASEÑA
    print("\n[PASO 3/3] Identificador de acceso")
    print("-" * 50)
    while True:
        pw = getpass.getpass("Contraseña (8+ alfanuméricos): ")
        if len(pw) >= 8 and pw.isalnum():
            break
        print("Error: Mínimo 8 caracteres sin símbolos.")
    
    # GUARDAR REGISTRO
    usuarios = cargar_datos(ARCHIVO_USUARIOS)
    usuarios.append({
        "nombre": nombre,
        "apellidos": apellidos,
        "num_empleado": num_empleado,  # ← Usamos el validado
        "password": pw
    })
    guardar_datos(ARCHIVO_USUARIOS, usuarios)
    print("\n✅ Registro exitoso. Ya puedes iniciar sesión.")

def iniciar_sesion():
    print("\n--- 🔓 INICIAR SESIÓN ---")
    max_intentos = 3
    intento = 0
    
    while intento < max_intentos:
        # PASO 1: VALIDAR NÚMERO DE EMPLEADO
        print(f"\n[Intento {intento + 1}/{max_intentos}]")
        num = validaciones.validar_acceso()  # ← VALIDACIÓN INTEGRADA
        
        if num is None:
            intento += 1
            print(f"🔄 Intentos restantes: {max_intentos - intento}\n")
            continue
        
        # PASO 2: VALIDAR CONTRASEÑA
        pw = getpass.getpass("Contraseña: ")
        
        # PASO 3: BUSCAR EN usuarios.json
        for u in cargar_datos(ARCHIVO_USUARIOS):
            if u["num_empleado"] == num and u["password"] == pw:
                print(f"\n✅ Bienvenido/a, {u['nombre']} {u['apellidos']} (ID: {u['num_empleado']})")
                return u
        
        intento += 1
        print("❌ Contraseña incorrecta.")
        if intento < max_intentos:
            print(f"🔄 Intentos restantes: {max_intentos - intento}\n")
    
    print(f"❌ Has agotado los {max_intentos} intentos. Vuelve al menú.")
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
    if not num_empleado or num_empleado == "Desconocido":
        return "Operario Desconocido"
        
    usuarios = cargar_datos(ARCHIVO_USUARIOS)
    
    for u in usuarios:
        if u["num_empleado"] == num_empleado:
            return f"👤 {u['nombre']} {u['apellidos']} (ID: {num_empleado})"
            
    return f"👤 Usuario no registrado (ID: {num_empleado})"