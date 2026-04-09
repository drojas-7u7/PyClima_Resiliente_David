"""
Módulo de Interfaz para PyClima - Sistema de Monitoreo Climático
Interfaz intuitiva y robusta para interacción del usuario
"""

import json
import os
import validaciones
import alertas
import persistencia
import auth
from datetime import datetime

class InterfazPyClima:
    """Interfaz intuitiva y robusta del Sistema PyClima"""
    
    def __init__(self, ruta_datos="datos_clima.json", usuario_actual=None):
        self.ruta_datos = ruta_datos
        self.datos = self._cargar_datos()
        self.zonas_validas = self._obtener_zonas()
        self.usuario_actual = usuario_actual  # Guardamos la identidad del operario en la clase
        
    def _cargar_datos(self):
        """Carga datos usando el módulo oficial de persistencia"""
        return persistencia.leer_historico()
    
    def _obtener_zonas(self):
        """Obtiene lista de zonas disponibles iterando sobre una LISTA"""
        zonas = set()
        for reg in self.datos:
            if "distrito" in reg:
                zonas.add(reg["distrito"])
        return sorted(list(zonas)) if zonas else []
    
    def _validar_duplicado(self, fecha, distrito):
        """Verifica si existe registro duplicado iterando sobre la LISTA"""
        for reg in self.datos:
            if reg.get("fecha") == str(fecha) and reg.get("distrito", "").lower() == distrito.lower():
                return True
        return False
    
    def _analizar_alertas(self, temperatura, humedad, viento):
        """Analiza y retorna alertas climáticas locales para visualización"""
        alertas = []
        if temperatura >= 35: alertas.append(f"🔴 ALERTA DE CALOR: {temperatura}°C")
        elif temperatura >= 30: alertas.append(f"🟡 ADVERTENCIA DE CALOR: {temperatura}°C")
        if viento >= 60: alertas.append(f"🔴 ALERTA DE VIENTO: {viento} km/h")
        elif viento >= 40: alertas.append(f"🟡 ADVERTENCIA DE VIENTO: {viento} km/h")
        if humedad >= 90: alertas.append(f"🔴 ALERTA DE LLUVIA: Humedad {humedad}%")
        return alertas
    
    def _mostrar_encabezado(self, titulo):
        print("\n" + "="*50)
        print(f"  {titulo}")
        print("="*50)
    
    def _mostrar_separador(self):
        print("-" * 50)
    
    def menu_principal(self):
        """Menú principal del sistema"""
        while True:
            self._mostrar_encabezado("🌡️  SISTEMA PYCLIMA RESILIENTE v3.0")
            print("1. 📝 Registrar Datos Climáticos")
            print("2. 📊 Consultar Datos (Por Zona)")
            print("3. 📈 Ver Histórico (Todas las Zonas)")
            print("4. 🚨 Alertas Activas")
            print("5. 🚪 Salir")
            self._mostrar_separador()
            
            opcion = input("Seleccione una opción (1-5): ").strip()
            
            if opcion == "1":
                self.registrar_datos()
            elif opcion == "2":
                self.consultar_datos()
            elif opcion == "3":
                self.ver_historico()
            elif opcion == "4":
                self.mostrar_panel_alertas()
            elif opcion == "5":
                self.salir()
                break
            else:
                print("❌ Opción no válida. Intente de nuevo.")
                input("Presione Enter para continuar...")
    
    def registrar_datos(self):
        """Flujo completo de registro con validaciones"""
        self._mostrar_encabezado("📝 REGISTRAR NUEVOS DATOS CLIMÁTICOS")
        self.datos = self._cargar_datos() # Refrescamos por si acaso
        
        while True:
            try:
                print("\n[1/5] FECHA DEL REGISTRO")
                fecha = validaciones.validar_fecha()
                
                print("\n[2/5] ZONA/DISTRITO")
                distrito = validaciones.validar_zona()
                if not distrito: return
                
                if self._validar_duplicado(fecha, distrito):
                    print(f"⚠️  Ya existe un registro para {distrito} en {fecha}")
                    if input("¿Desea ingresar datos nuevamente? (s/n): ").lower() != 's': return
                    continue
                
                print("\n[3/5] TEMPERATURA")
                temperatura = validaciones.validar_temperatura()
                
                print("\n[4/5] HUMEDAD")
                humedad = validaciones.validar_humedad()
                
                print("\n[5/5] VELOCIDAD DEL VIENTO")
                viento = validaciones.validar_viento()
                
                print("\n" + "="*50)
                print("✅ DATOS VALIDADOS EXITOSAMENTE")
                print("="*50)
                
                umbrales = persistencia.obtener_umbrales_alerta()
                datos_registro = {"temperatura": temperatura, "humedad": humedad, "viento": viento}
                alertas_activas = alertas.evaluar_alertas(datos_registro, umbrales)
                
                # --- PASO 1: MOSTRAR ALERTAS ANTES DE GUARDAR ---
                if alertas_activas:
                    print("\n🚨 ALERTAS PRELIMINARES DETECTADAS:")
                    for alerta in alertas_activas: 
                        print(f"   {alerta}")
                else:
                    print("\n✅ Niveles climáticos normales (Sin alertas)")
                print("-" * 50)
                # ------------------------------------------------

                nuevo_registro = {
                    "fecha": fecha,
                    "distrito": distrito,
                    "temperatura": temperatura, 
                    "temp": temperatura,        
                    "humedad": humedad,
                    "viento": viento,
                    "lluvia": 0.0,
                    "alertas": alertas_activas,
                    "registrado_por": self.usuario_actual["num_empleado"] if self.usuario_actual else "Desconocido",
                    "editado": False
                }
                
                # Aquí el sistema saltará a persistencia.py y hará la pregunta de confirmación
                exito = persistencia.registrar_nuevo_dato(nuevo_registro)
                
                if exito:
                    self._mostrar_separador()
                    if input("\n¿Registrar otro dato? (s/n): ").strip().lower() != 's': return
                else:
                    return
                    
            except KeyboardInterrupt:
                print("\n\n❌ Registro cancelado por el usuario")
                return
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                if input("¿Desea ingresar los datos nuevamente? (s/n): ").lower() != 's': return
    
    def consultar_datos(self):
        """Menú avanzado de consultas con filtros y opciones posteriores"""
        while True:
            self._mostrar_encabezado("📊 CONSULTAR DATOS AVANZADO")
            self.datos = self._cargar_datos() # Refrescar datos
            
            if not self.datos:
                print("❌ No hay datos registrados en el sistema.")
                input("Presione Enter para continuar...")
                return
                
            print("1. 📍 Filtrar por Zona/Distrito")
            print("2. 📅 Filtrar por Fecha")
            print("3. 👤 Filtrar por Usuario (Mis registros / Editar)")
            print("4. ⬅️  Volver al menú principal")
            self._mostrar_separador()
            
            opcion = input("Seleccione un filtro (1-4): ").strip()
            
            if opcion == "1":
                self._menu_consultar_zona()
            elif opcion == "2":
                self._menu_consultar_fecha()
            elif opcion == "3":
                self._menu_consultar_usuario()
            elif opcion == "4":
                break # Sale del bucle y vuelve al menú principal
            else:
                print("❌ Opción no válida.")
                continue # Vuelve a mostrar el menú de consultas
                
            # -----------------------------------------
            # OPCIONES POSTERIORES (Según el esquema)
            # -----------------------------------------
            if opcion in ["1", "2", "3"]:
                print("\n" + "="*50)
                print("OPCIONES POSTERIORES:")
                print("1. Hacer otra consulta")
                print("2. Volver al menú principal")
                print("3. Salir del sistema")
                
                post_opcion = input("¿Qué desea hacer ahora? (1-3): ").strip()
                
                if post_opcion == "2":
                    break # Rompe el bucle de consultas, vuelve al principal
                elif post_opcion == "3":
                    self.salir()
                    exit() # Cierra el programa por completo
                # Si elige "1", el bucle while True vuelve a empezar solo

    def _menu_consultar_zona(self):
        """Lógica extraída para buscar por zona"""
        self.zonas_validas = self._obtener_zonas()
        print("\n📍 Zonas disponibles:")
        for i, zona in enumerate(self.zonas_validas, 1): 
            print(f"   {i}. {zona}")
        
        try:
            seleccion = int(input("\nSeleccione una zona (número): ")) - 1
            if 0 <= seleccion < len(self.zonas_validas):
                zona_seleccionada = self.zonas_validas[seleccion]
                self._mostrar_datos_zona(zona_seleccionada)
            else:
                print("❌ Selección inválida")
        except ValueError:
            print("❌ Ingrese un número válido")

    def _menu_consultar_fecha(self):
        """Lógica extraída para buscar por fecha exacta"""
        print("\n📅 BÚSQUEDA POR FECHA")
        # ¡Aquí usamos tu módulo DEV 2 para garantizar el formato AAAA-MM-DD!
        fecha_buscada = validaciones.validar_fecha()
        
        print(f"\n📊 Datos del día: {fecha_buscada}")
        self._mostrar_separador()
        
        encontrados = 0
        for reg in self.datos:
            if reg.get("fecha") == fecha_buscada:
                encontrados += 1
                temp = reg.get('temp', reg.get('temperatura', 0))
                print(f"📍 Zona: {reg.get('distrito', 'Desconocida')}")
                print(f"   🌡️  Temperatura: {temp}°C")
                print(f"   💧 Humedad: {reg.get('humedad', 0)}%")
                print(f"   💨 Viento: {reg.get('viento', 0)} km/h")
                
                alertas_locales = self._analizar_alertas(temp, reg.get('humedad', 0), reg.get('viento', 0))
                for alerta in alertas_locales: 
                    print(f"   {alerta}")
                print("-" * 30)
                
        if encontrados == 0:
            print(f"❌ No hay datos registrados para la fecha {fecha_buscada}")
        else:
            print(f"✅ Total de registros encontrados: {encontrados}")
    
    def _menu_consultar_usuario(self):
        """Lógica extraída para buscar por operario usando el traductor"""
        print("\n👤 BÚSQUEDA POR OPERARIO")
        
        # 1. Escanear el JSON para ver quién ha participado
        operarios_ids = set()
        for reg in self.datos:
            if "registrado_por" in reg:
                operarios_ids.add(reg["registrado_por"])
                
        lista_operarios = list(operarios_ids)
        
        if not lista_operarios:
            print("❌ No hay registros asociados a ningún operario.")
            return

        # 2. Mostrar el directorio usando la función traductora de auth.py
        print("\n📋 Directorio de operarios con registros:")
        for i, op_id in enumerate(lista_operarios, 1):
            nombre_completo = auth.obtener_nombre_operario(op_id)
            
            # --- NUEVA LÓGICA DE RESALTADO ---
            # Verificamos si hay un usuario logueado y si su número coincide con el de la lista
            if self.usuario_actual and op_id == self.usuario_actual.get("num_empleado"):
                print(f"   {i}. {nombre_completo}  ⬅️  (ESTE ERES TÚ)")
            else:
                print(f"   {i}. {nombre_completo}")
            
        # 3. Selección y filtrado
        try:
            seleccion = int(input("\nSeleccione un operario (número): ")) - 1
            if 0 <= seleccion < len(lista_operarios):
                op_seleccionado = lista_operarios[seleccion]
                nombre_seleccionado = auth.obtener_nombre_operario(op_seleccionado)
                
                print(f"\n📊 Datos registrados por: {nombre_seleccionado}")
                self._mostrar_separador()
                
                encontrados = 0
                for reg in self.datos:
                    if reg.get("registrado_por") == op_seleccionado:
                        encontrados += 1
                        temp = reg.get('temp', reg.get('temperatura', 0))
                        print(f"📅 {reg.get('fecha')} | 📍 {reg.get('distrito', 'Desconocida')}")
                        print(f"   🌡️  T: {temp}°C | 💧 H: {reg.get('humedad', 0)}% | 💨 V: {reg.get('viento', 0)} km/h")
                        print("-" * 30)
                        
                print(f"✅ Total de registros de este operario: {encontrados}")
            else:
                print("❌ Selección inválida")
        except ValueError:
            print("❌ Ingrese un número válido")
    
    def _mostrar_datos_zona(self, zona):
        """Muestra todos los datos de una zona iterando sobre la LISTA"""
        print(f"\n📊 Datos de: {zona}")
        self._mostrar_separador()
        
        encontrados = 0
        for reg in self.datos:
            if reg.get("distrito", "").lower() == zona.lower():
                encontrados += 1
                temp = reg.get('temp', reg.get('temperatura', 0))
                print(f"📅 {reg['fecha']}")
                print(f"   🌡️  Temperatura: {temp}°C")
                print(f"   💧 Humedad: {reg['humedad']}%")
                print(f"   💨 Viento: {reg['viento']} km/h")
                
                alertas_locales = self._analizar_alertas(temp, reg['humedad'], reg['viento'])
                for alerta in alertas_locales: print(f"   {alerta}")
                print()
        
        if encontrados == 0: print(f"❌ No hay datos para {zona}")
        else: print(f"✅ Total de registros: {encontrados}")
    
    def ver_historico(self):
        """Muestra histórico completo con autoría detallada y opciones de filtrado"""
        while True:
            self._mostrar_encabezado("📈 HISTÓRICO COMPLETO DE TODAS LAS ZONAS")
            self.datos = self._cargar_datos() # Refrescar
            
            if not self.datos:
                print("❌ No hay datos registrados en el sistema.")
                input("Presione Enter para continuar...")
                return
                
            print(f"\n{'='*50}")
            for reg in self.datos:
                temp = reg.get('temp', reg.get('temperatura', 0))
                
                # --- TRADUCTOR DE IDENTIDADES EN ACCIÓN ---
                operario_id = reg.get("registrado_por", "Desconocido")
                nombre_operario = auth.obtener_nombre_operario(operario_id)
                
                print(f"📅 {reg['fecha']} | 📍 {reg.get('distrito', 'Desconocida')}")
                print(f"   🌡️  T: {temp}°C | 💧 H: {reg.get('humedad', 0)}% | 💨 V: {reg.get('viento', 0)} km/h")
                
                # Imprimimos el autor
                print(f"   {nombre_operario}")
                # Avisamos si el registro sufrió una corrección
                if reg.get("editado"):
                    print("   ⚠️ (Este registro ha sido editado/corregido)")
                    
                self._mostrar_separador()
            
            print(f"✅ Total de registros en la base de datos: {len(self.datos)}")
            print(f"{'='*50}")
            
            # --- SUBMENÚ DE NAVEGACIÓN Y FILTROS (Punto 7) ---
            print("\nOPCIONES DE HISTÓRICO:")
            print("1. 🔍 Aplicar filtros de búsqueda (Zona / Fecha / Usuario)")
            print("2. ⬅️  Volver al menú principal")
            
            opcion = input("¿Qué desea hacer ahora? (1-2): ").strip()
            
            if opcion == "1":
                # Como ya programamos un menú de filtros genial en la Fase B, lo reciclamos
                self.consultar_datos()
                break # Al salir de las consultas, volvemos al menú principal para no imprimir el histórico gigante otra vez
            elif opcion == "2":
                break
            else:
                print("❌ Opción no válida. Por favor, seleccione 1 o 2.")
                input("Presione Enter para intentarlo de nuevo...")
    
    def mostrar_panel_alertas(self):
        """Panel de alertas activas con filtros y navegación avanzada (Fase D)"""
        while True:
            self._mostrar_encabezado("🚨 PANEL DE ALERTAS ACTIVAS")
            self.datos = self._cargar_datos() # Refrescar
            alertas_encontradas = []

            # 1. Recopilamos las alertas actuales
            for reg in self.datos:
                temp = reg.get('temp', reg.get('temperatura', 0))
                alertas_locales = self._analizar_alertas(temp, reg.get('humedad', 0), reg.get('viento', 0))
                if alertas_locales:
                    alertas_encontradas.append({
                        'zona': reg.get('distrito', 'Desconocida'),
                        'fecha': reg['fecha'],
                        'alertas': alertas_locales
                    })
            
            if not alertas_encontradas:
                print("\n✅ No hay alertas activas en ningún distrito en este momento.")
                input("\nPresione Enter para volver al menú principal...")
                break

            # 2. Extraemos los tipos de alerta únicos para crear el filtro dinámico
            tipos_alertas = set()
            for item in alertas_encontradas:
                for alerta in item['alertas']:
                    tipos_alertas.add(alerta)
            lista_tipos = list(tipos_alertas)

            # 3. Mostrar menú principal del panel de alertas
            print(f"\n⚠️  Se detectaron {len(alertas_encontradas)} zonas con alertas activas.")
            print("\nOPCIONES DEL PANEL:")
            print("1. 👁️  Ver TODAS las alertas activas")
            print("2. 🔍 Filtrar por tipo de alerta")
            print("3. ⬅️  Volver al menú principal")
            print("4. 🚪 Salir del sistema")
            
            opcion = input("\nSeleccione una opción (1-4): ").strip()
            
            if opcion == "1":
                self._imprimir_alertas(alertas_encontradas)
                # Mostramos menú posterior y comprobamos si quiere volver al menú principal
                if self._menu_post_alerta() == "menu_principal": break
                
            elif opcion == "2":
                accion = self._filtrar_y_mostrar_alertas(alertas_encontradas, lista_tipos)
                if accion == "menu_principal": break
                
            elif opcion == "3":
                break # Rompe el bucle y vuelve al menú principal
                
            elif opcion == "4":
                self.salir()
                exit()
            else:
                print("❌ Opción no válida.")

    def _imprimir_alertas(self, lista_alertas):
        """Función auxiliar para imprimir las alertas de forma estructurada"""
        print("\n" + "="*50)
        for item in lista_alertas:
            print(f"📍 ZONA: {item['zona']} | 📅 FECHA: {item['fecha']}")
            print("-" * 45)
            for alerta in item['alertas']: 
                print(f"  → {alerta}")
        print("="*50)

    def _filtrar_y_mostrar_alertas(self, alertas_encontradas, lista_tipos):
        """Maneja el filtrado de alertas y lanza la navegación posterior"""
        print("\n🚨 TIPOS DE ALERTA ACTUALMENTE ACTIVOS:")
        for i, tipo in enumerate(lista_tipos, 1):
            print(f"   {i}. {tipo}")
            
        # --- AÑADIMOS LA OPCIÓN DE ESCAPE (Dinámica) ---
        opcion_volver = len(lista_tipos) + 1
        print(f"   {opcion_volver}. 🔙 Volver al panel de alertas")
            
        try:
            entrada = input(f"\nSeleccione la alerta que desea investigar (1-{opcion_volver}) [o 'c' para cancelar]: ").strip()
            
            # Si usa el truco de la Fase B para cancelar
            if entrada.lower() == 'c':
                return "panel_alertas"
                
            seleccion = int(entrada)
            
            # Si elige la opción extra de volver
            if seleccion == opcion_volver:
                return "panel_alertas"
                
            # Si elige una alerta válida
            elif 1 <= seleccion <= len(lista_tipos):
                alerta_buscada = lista_tipos[seleccion - 1]
                
                # Filtramos la lista buscando la alerta exacta
                filtradas = [item for item in alertas_encontradas if alerta_buscada in item['alertas']]
                
                print(f"\n📊 Resultados filtrados para: {alerta_buscada}")
                self._imprimir_alertas(filtradas)
                
                return self._menu_post_alerta()
            else:
                print("❌ Selección inválida.")
                return "panel_alertas"
                
        except ValueError:
            print("❌ Ingrese un número válido.")
            return "panel_alertas"

    def _menu_post_alerta(self):
        """Submenú de navegación posterior exigido por el esquema (Punto 8)"""
        while True:
            print("\nOPCIONES POSTERIORES:")
            print("1. 🔙 Volver al panel de alertas")
            print("2. ⬅️  Volver al menú principal")
            print("3. 🚪 Salir del sistema")
            
            post_opcion = input("¿Qué desea hacer ahora? (1-3): ").strip()
            
            if post_opcion == "1":
                return "panel_alertas" # Hace que el bucle padre vuelva a empezar
            elif post_opcion == "2":
                return "menu_principal" # Avisa al bucle padre para que se rompa
            elif post_opcion == "3":
                self.salir()
                exit()
            else:
                print("❌ Opción no válida.")
    
    def salir(self):
        self._mostrar_encabezado("🚪 CERRANDO SISTEMA")
        print("\n✅ Todos los datos han sido guardados correctamente")
        print("🌍 ¡Gracias por usar PyClima Resiliente!")
        print("👋 ¡Hasta pronto!\n")