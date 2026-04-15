import json
import os
import getpass
import validaciones
import alertas
import persistencia
import pwinput

DB_EMPLEADOS = 'empleados.json'
ARCHIVO_USUARIOS = 'usuarios.json' #Carga de archivos a utilizar
ARCHIVO_CLIMA = 'datos_clima.json'

def cargar_datos(archivo): #Valida la existencia del archivo y su formato correcto, para evitar errores posteriores al cargar datos
    if not os.path.exists(archivo): return []
    try:
        with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️ Advertencia: El archivo '{archivo}' está corrupto o tiene formato inválido ⚠️")
        return []
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo leer '{archivo}': {e} ⚠️")
        return []

def guardar_datos(archivo, datos): #Función para guardar datos en formato JSON, con manejo de errores
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def _obtener_temperatura_registro(registro): #Función auxiliar para obtener la temperatura de un registro, considerando posibles variaciones en la clave (temp o temperatura)
    return registro.get("temp", registro.get("temperatura", 0))

def _pedir_float_editable(mensaje, valor_actual, minimo=None, maximo=None):   #Función auxiliar para pedir un valor numérico editable, con validación de rango y formato, y opción de mantener el valor actual
    while True:
        entrada = input(f"{mensaje} (actual: {valor_actual}) [Enter para mantener]: ").strip()
        if not entrada:
            return float(valor_actual)

        try:
            valor = float(entrada)
        except ValueError:
            print("❌ Error: Debes introducir un valor numérico válido ❌")
            continue

        if minimo is not None and valor < minimo:
            print(f"⚠️ Error: El valor no puede ser menor que {minimo} ⚠️")
            continue
        if maximo is not None and valor > maximo:
            print(f"⚠️ Error: El valor no puede ser mayor que {maximo} ⚠️")
            continue

        return valor

def _pedir_distrito_editable(distrito_actual): #Función auxiliar para pedir un distrito editable, validando contra la lista de distritos oficiales en config.json, y opción de mantener el valor actual
    try:
        with open("config.json", "r", encoding="utf-8") as archivo:
            distritos = json.load(archivo).get("distritos_oficiales", [])
    except (FileNotFoundError, json.JSONDecodeError):
        print("❌ No se pudo validar el distrito mencionado en la base de datos ❌")
        return distrito_actual

    mapa = {d.lower(): d for d in distritos}

    while True:
        entrada = input(f"Nuevo distrito (actual: {distrito_actual}) [Enter para mantener]: ").strip()
        if not entrada:
            return distrito_actual

        zona_normalizada = entrada.lower()
        if zona_normalizada in mapa:
            return mapa[zona_normalizada]

        print("⚠️ Distrito no reconocido. Introduce un distrito oficial o pulsa Enter para mantener el actual ⚠️")

def imprimir_detalle(r, idx=None):    #Función para imprimir el detalle de un registro de clima, con formato legible, mostrando alertas y si el registro ha sido editado
    id_txt = f"ID: {idx} | " if idx is not None else ""
    edit_txt = " [EDITADO]" if r.get("editado") else ""
    alertas = ", ".join(r.get("alertas", [])) if r.get("alertas") else "Ninguna"
    print(f"{id_txt}Fecha: {r['fecha']} | Distrito: {r['distrito']} | Zona: {r.get('zona', 'N/A')}")
    print(f"      Temp: {_obtener_temperatura_registro(r)}°C | Hum: {r['humedad']}% | Viento: {r['viento']}km/h")
    print(f"      Lluvia: {r['lluvia']}mm | Alertas: {alertas}{edit_txt}")
    print("-" * 75)

def registrar_usuario():   #Función para registrar un nuevo usuario, validando que el número de empleado exista en empleados.json
    try:
        print("\n--- REGISTRO DE NUEVO USUARIO ---")

        # PASO 1: VALIDAR QUE SEA EMPLEADO AUTORIZADO (empleados.json)
        print("\n[PASO 1/3] Verificación de autenticidad del empleado")
        print("-" * 50)
        num_empleado = validaciones.validar_acceso()  # Valida unicamente empleados.json

        if num_empleado is None:
            print("❌ No se puede continuar sin un número de empleado válido ❌")
            return  # Cancela el registro

        usuarios = cargar_datos(ARCHIVO_USUARIOS)
        if any(u.get("num_empleado") == num_empleado for u in usuarios):
            print("⚠️ Este número de empleado ya tiene un usuario registrado ⚠️")
            return

        # PASO 2: RECOPILAR DATOS PERSONALES
        print("\n[PASO 2/3] Información personal")
        print("-" * 50)
        nombre = input("Nombre: ").strip()
        apellidos = input("Apellidos: ").strip()

        if not nombre or not apellidos:
            print("❌ Error: Nombre y apellidos no pueden estar vacíos ❌")
            return

        # PASO 3: ESTABLECER CONTRASEÑA
        print("\n[PASO 3/3] Identificador de acceso")
        print("-" * 50)
        while True:
            pw = pwinput.pwinput("Contraseña (8+ alfanuméricos): ", mask='*')
            if len(pw) >= 8 and pw.isalnum():
                break
            print("❌ Error: Mínimo 8 caracteres sin símbolos ❌")

        # GUARDAR REGISTRO
        usuarios.append({
            "nombre": nombre,
            "apellidos": apellidos,
            "num_empleado": num_empleado,  
            "password": pw
        })
        guardar_datos(ARCHIVO_USUARIOS, usuarios)
        print("\n✅ Registro exitoso. Ya puedes iniciar sesión ✅")

    except Exception as e:
        print(f"❌ Error durante el registro: {e} ❌")
        print("Por favor, intenta de nuevo.")

def iniciar_sesion():
    print("\n--- 🔓 INICIAR SESIÓN ---")
    max_intentos_pw = 3
    intento_pw = 0

    # PASO 1: VALIDAR NÚMERO DE USUARIO REGISTRADO (contra usuarios.json)
    num = validaciones.validar_usuario_sesion()  # Valida SOLO contra usuarios.json

    if num is None:
        print("❌ No se pudo validar el usuario. Vuelve al menú principal ❌")
        return None

    # PASO 2: VALIDAR CONTRASEÑA (máximo 3 intentos)
    while intento_pw < max_intentos_pw:
        pw = pwinput.pwinput(f"Contraseña [{intento_pw + 1}/{max_intentos_pw}]: ", mask='*')

        # PASO 3: BUSCAR EN usuarios.json
        for u in cargar_datos(ARCHIVO_USUARIOS):
            if u["num_empleado"] == num and u["password"] == pw:
                print(f"\n👋 Bienvenido/a, {u['nombre']} {u['apellidos']} (ID: {u['num_empleado']}) 👋")
                return u

        intento_pw += 1
        if intento_pw < max_intentos_pw:
            print("❌ Contraseña incorrecta. Intenta de nuevo.")
            print(f"🔄 Intentos restantes: {max_intentos_pw - intento_pw}\n")

    print(f"❌ Has agotado los {max_intentos_pw} intentos de contraseña. Vuelve al menú principal ❌")
    return None

def consultar_y_editar_historial(num_empleado): #Función para que un usuario pueda consultar sus registros de clima y editar uno de ellos.
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
            print("❌ ERROR: Este registro ya fue corregido anteriormente y está bloqueado ❌")
        else:
            print(f"\n Vas a editar TODO el registro de {registros[idx]['distrito']} del día {registros[idx]['fecha']}.")
            confirmar = input("¿Estás seguro de que quieres continuar? Solo podrás hacerlo UNA VEZ (si/no): ").strip().lower()
            
            if confirmar == "si":
                try:
                    print("\n--- INTRODUCE LOS NUEVOS DATOS CORRECTOS ---")

                    distrito_actual = registros[idx].get("distrito", "")
                    temp_actual = _obtener_temperatura_registro(registros[idx])
                    humedad_actual = registros[idx].get("humedad", 0)
                    viento_actual = registros[idx].get("viento", 0)
                    lluvia_actual = registros[idx].get("lluvia", 0)

                    distrito_final = _pedir_distrito_editable(distrito_actual)
                    temp_final = _pedir_float_editable("Nueva Temperatura", temp_actual, -20, 50)
                    humedad_final = _pedir_float_editable("Nueva Humedad %", humedad_actual, 0, 100)
                    viento_final = _pedir_float_editable("Nueva Velocidad del Viento km/h", viento_actual, 0, 150)
                    lluvia_final = _pedir_float_editable("Nueva Lluvia mm", lluvia_actual, 0)

                    for i, reg in enumerate(registros):
                        if i != idx and reg.get("fecha") == registros[idx].get("fecha") and reg.get("distrito", "").lower() == distrito_final.lower():
                            print("❌ La corrección generaría un duplicado para esa fecha y distrito ❌")
                            return

                    umbrales = persistencia.obtener_umbrales_alerta()
                    alertas_activas = alertas.evaluar_alertas({
                        "temperatura": temp_final,
                        "humedad": humedad_final,
                        "viento": viento_final,
                        "lluvia": lluvia_final,
                    }, umbrales)

                    registros[idx]["distrito"] = distrito_final
                    registros[idx]["temp"] = temp_final
                    registros[idx]["temperatura"] = temp_final
                    registros[idx]["humedad"] = humedad_final
                    registros[idx]["viento"] = viento_final
                    registros[idx]["lluvia"] = lluvia_final
                    registros[idx]["alertas"] = alertas_activas
                    registros[idx]["editado"] = True 
                    
                    guardar_datos(ARCHIVO_CLIMA, registros)
                    print("\nRegistro corregido y guardado con éxito.")
                    
                except ValueError:
                    print("❌ Error: Has introducido un formato de número incorrecto. No se guardaron los cambios ❌")
            else:
                print("Operación cancelada.")

def consultar_por_distrito():    #Función para consultar registros por distrito
    distrito = input("Distrito: ").strip().title()
    for r in cargar_datos(ARCHIVO_CLIMA):
        if r.get("distrito") == distrito: imprimir_detalle(r)

def consultar_por_fecha():  #Función para consultar registros por fecha
    fecha = input("Fecha (YYYY-MM-DD): ")
    for r in cargar_datos(ARCHIVO_CLIMA):
        if r.get("fecha") == fecha: imprimir_detalle(r)

def obtener_nombre_operario(num_empleado):  #Función para obtener el nombre del operario a partir de su número de empleado
    if not num_empleado or num_empleado == "Desconocido":
        return "Operario Desconocido"
        
    usuarios = cargar_datos(ARCHIVO_USUARIOS)
    
    for u in usuarios:
        if u["num_empleado"] == num_empleado:
            return f"👤 {u['nombre']} {u['apellidos']} (ID: {num_empleado})"
            
    return f"👤 Usuario no registrado (ID: {num_empleado})"
