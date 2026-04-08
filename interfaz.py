"""
Módulo de Interfaz para PyClima - Sistema de Monitoreo Climático
Interfaz intuitiva y robusta para interacción del usuario
"""

import json
import os
from datetime import datetime
from pathlib import Path


class InterfazPyClima:
    """Interfaz intuitiva y robusta del Sistema PyClima"""
    
    def __init__(self, ruta_datos="datos_clima.json"):
        self.ruta_datos = ruta_datos
        self.datos = self._cargar_datos()
        self.zonas_validas = self._obtener_zonas()
        
    def _cargar_datos(self):
        """Carga datos existentes desde JSON"""
        if os.path.exists(self.ruta_datos):
            try:
                with open(self.ruta_datos, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _guardar_datos(self):
        """Guarda datos en formato JSON"""
        try:
            with open(self.ruta_datos, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"❌ Error al guardar datos: {e}")
            return False
    
    def _obtener_zonas(self):
        """Obtiene lista de zonas disponibles"""
        zonas = set()
        for registros in self.datos.values():
            if isinstance(registros, list):
                for reg in registros:
                    if "distrito" in reg:
                        zonas.add(reg["distrito"])
        return sorted(list(zonas)) if zonas else []
    
    def _validar_fecha(self, fecha_str):
        """Valida formato de fecha DD/MM/AAAA"""
        try:
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            return fecha, None
        except ValueError:
            return None, "❌ Formato de fecha inválido. Use DD/MM/AAAA"
    
    def _validar_temperatura(self, temp):
        """Valida rango de temperatura (-50°C a 60°C)"""
        try:
            valor = float(temp)
            if -50 <= valor <= 60:
                return valor, None
            return None, "❌ Temperatura fuera de rango (-50°C a 60°C)"
        except ValueError:
            return None, "❌ La temperatura debe ser un número decimal"
    
    def _validar_humedad(self, humedad):
        """Valida rango de humedad (0% a 100%)"""
        try:
            valor = float(humedad)
            if 0 <= valor <= 100:
                return valor, None
            return None, "❌ Humedad fuera de rango (0% a 100%)"
        except ValueError:
            return None, "❌ La humedad debe ser un número decimal"
    
    def _validar_viento(self, viento):
        """Valida velocidad del viento (0 a 200 km/h)"""
        try:
            valor = int(viento)
            if 0 <= valor <= 200:
                return valor, None
            return None, "❌ Velocidad de viento fuera de rango (0-200 km/h)"
        except ValueError:
            return None, "❌ La velocidad debe ser un número entero"
    
    def _validar_duplicado(self, fecha, distrito):
        """Verifica si existe registro duplicado"""
        key_fecha = str(fecha)
        if key_fecha in self.datos:
            for reg in self.datos[key_fecha]:
                if reg.get("distrito", "").lower() == distrito.lower():
                    return True
        return False
    
    def _analizar_alertas(self, temperatura, humedad, viento):
        """Analiza y retorna alertas climáticas"""
        alertas = []
        
        # Alerta de Calor
        if temperatura >= 35:
            alertas.append(f"🔴 ALERTA DE CALOR: {temperatura}°C - Peligro extremo")
        elif temperatura >= 30:
            alertas.append(f"🟡 ADVERTENCIA DE CALOR: {temperatura}°C")
        
        # Alerta de Viento
        if viento >= 60:
            alertas.append(f"🔴 ALERTA DE VIENTO: {viento} km/h - Peligro extremo")
        elif viento >= 40:
            alertas.append(f"🟡 ADVERTENCIA DE VIENTO: {viento} km/h")
        
        # Alerta de Lluvia (Humedad extrema sugiere lluvia)
        if humedad >= 90:
            alertas.append(f"🔴 ALERTA DE LLUVIA: Humedad {humedad}% - Lluvia probable")
        elif humedad >= 75:
            alertas.append(f"🟡 ADVERTENCIA DE LLUVIA: Humedad {humedad}%")
        
        return alertas
    
    def _mostrar_encabezado(self, titulo):
        """Muestra encabezado formateado"""
        print("\n" + "="*50)
        print(f"  {titulo}")
        print("="*50)
    
    def _mostrar_separador(self):
        """Muestra una línea separadora"""
        print("-"*50)
    
    def menu_principal(self):
        """Menú principal del sistema"""
        while True:
            self._mostrar_encabezado("🌡️  SISTEMA PYCLIMA RESILIENTE v2.0")
            print("1. 📝 Registrar Datos Climáticos")
            print("2. 📊 Consultar Datos (Por Zona)")
            print("3. 📈 Ver Histórico (Todas las Zonas)")
            print("4. � Alertas Activas")
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
        
        while True:
            try:
                # 1️⃣ Validación de Fecha
                print("\n[1/5] FECHA DEL REGISTRO")
                fecha_input = input("📅 Ingrese la fecha (DD/MM/AAAA): ").strip()
                fecha, error = self._validar_fecha(fecha_input)
                if error:
                    print(error)
                    continue
                
                # 2️⃣ Validación de Distrito (Zona)
                print("\n[2/5] ZONA/DISTRITO")
                distrito = input("📍 Ingrese el distrito/zona: ").strip()
                if not distrito or len(distrito) < 2:
                    print("❌ El distrito debe tener al menos 2 caracteres")
                    continue
                
                # Verificar duplicado
                if self._validar_duplicado(fecha, distrito):
                    print(f"⚠️  Ya existe un registro para {distrito} en {fecha}")
                    reintentar = input("¿Desea ingresar datos nuevamente? (s/n): ").lower()
                    if reintentar != 's':
                        print("❌ Operación cancelada")
                        return
                    continue
                
                # 3️⃣ Validación de Temperatura
                print("\n[3/5] TEMPERATURA")
                print("   Rango válido: -50°C a 60°C")
                temp_input = input("🌡️  Ingrese la temperatura (°C): ").strip()
                temperatura, error = self._validar_temperatura(temp_input)
                if error:
                    print(error)
                    continue
                
                # 4️⃣ Validación de Humedad
                print("\n[4/5] HUMEDAD")
                print("   Rango válido: 0% a 100%")
                humedad_input = input("💧 Ingrese la humedad relativa (%): ").strip()
                humedad, error = self._validar_humedad(humedad_input)
                if error:
                    print(error)
                    continue
                
                # 5️⃣ Validación de Viento
                print("\n[5/5] VELOCIDAD DEL VIENTO")
                print("   Rango válido: 0 a 200 km/h")
                viento_input = input("💨 Ingrese la velocidad del viento (km/h): ").strip()
                viento, error = self._validar_viento(viento_input)
                if error:
                    print(error)
                    continue
                
                # ✅ Todos los datos válidos
                print("\n" + "="*50)
                print("✅ DATOS VALIDADOS EXITOSAMENTE")
                print("="*50)
                
                # 🔍 Analizar Alertas
                alertas = self._analizar_alertas(temperatura, humedad, viento)
                
                # 💾 Guardar Datos
                key_fecha = str(fecha)
                if key_fecha not in self.datos:
                    self.datos[key_fecha] = []
                
                registro = {
                    "distrito": distrito,
                    "temperatura": temperatura,
                    "humedad": humedad,
                    "viento": viento,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.datos[key_fecha].append(registro)
                
                if self._guardar_datos():
                    print(f"\n✅ Registro guardado exitosamente")
                    print(f"   📍 Distrito: {distrito}")
                    print(f"   📅 Fecha: {fecha}")
                    print(f"   🌡️  Temperatura: {temperatura}°C")
                    print(f"   💧 Humedad: {humedad}%")
                    print(f"   💨 Viento: {viento} km/h")
                    
                    # Mostrar alertas si las hay
                    if alertas:
                        print("\n🚨 ALERTAS DETECTADAS:")
                        for alerta in alertas:
                            print(f"   {alerta}")
                    else:
                        print("\n   ✅ Niveles climáticos normales")
                    
                    self._mostrar_separador()
                    print("💾 Datos guardados en JSON")
                    
                    continuar = input("\n¿Registrar otro dato? (s/n): ").lower()
                    if continuar != 's':
                        print("↩️  Volviendo al menú principal...")
                        return
                    print("\n")
                else:
                    print("❌ Error al guardar los datos")
                    return
                    
            except KeyboardInterrupt:
                print("\n\n❌ Registro cancelado por el usuario")
                return
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                reintentar = input("¿Desea ingresar los datos nuevamente? (s/n): ").lower()
                if reintentar != 's':
                    return
    
    def consultar_datos(self):
        """Consulta datos por zona"""
        self._mostrar_encabezado("📊 CONSULTAR DATOS POR ZONA")
        
        if not self.datos:
            print("❌ No hay datos registrados")
            input("Presione Enter para continuar...")
            return
        
        # Actualizar zonas
        self.zonas_validas = self._obtener_zonas()
        
        if not self.zonas_validas:
            print("❌ No hay zonas disponibles")
            input("Presione Enter para continuar...")
            return
        
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
        
        input("\nPresione Enter para volver al menú...")
    
    def _mostrar_datos_zona(self, zona):
        """Muestra todos los datos de una zona"""
        print(f"\n📊 Datos de: {zona}")
        self._mostrar_separador()
        
        encontrados = 0
        for fecha, registros in sorted(self.datos.items()):
            for reg in registros:
                if reg.get("distrito", "").lower() == zona.lower():
                    encontrados += 1
                    print(f"📅 {fecha}")
                    print(f"   🌡️  Temperatura: {reg['temperatura']}°C")
                    print(f"   💧 Humedad: {reg['humedad']}%")
                    print(f"   💨 Viento: {reg['viento']} km/h")
                    
                    # Analizar alertas para este registro
                    alertas = self._analizar_alertas(
                        reg['temperatura'], 
                        reg['humedad'], 
                        reg['viento']
                    )
                    if alertas:
                        for alerta in alertas:
                            print(f"   {alerta}")
                    print()
        
        if encontrados == 0:
            print(f"❌ No hay datos para {zona}")
        else:
            print(f"✅ Total de registros: {encontrados}")
    
    def ver_historico(self):
        """Muestra histórico completo de todas las zonas"""
        self._mostrar_encabezado("📈 HISTÓRICO COMPLETO DE TODAS LAS ZONAS")
        
        if not self.datos:
            print("❌ No hay datos registrados")
            input("Presione Enter para continuar...")
            return
        
        total_registros = 0
        for fecha, registros in sorted(self.datos.items()):
            print(f"\n📅 Fecha: {fecha}")
            self._mostrar_separador()
            for reg in registros:
                total_registros += 1
                print(f"   📍 {reg['distrito']}")
                print(f"      🌡️  T: {reg['temperatura']}°C | 💧 H: {reg['humedad']}% | 💨 V: {reg['viento']} km/h")
        
        print(f"\n{'='*50}")
        print(f"✅ Total de registros: {total_registros}")
        print(f"{'='*50}")
        
        input("\nPresione Enter para volver al menú...")
    
    def mostrar_panel_alertas(self):
        """Panel de alertas activas - Muestra todas las alertas detectadas"""
        self._mostrar_encabezado("🚨 PANEL DE ALERTAS ACTIVAS")
        
        hay_alertas = False
        alertas_encontradas = []

        # Recorrer todos los registros
        for fecha, registros in self.datos.items():
            for registro in registros:
                # Evaluar alertas del registro
                alertas = self._analizar_alertas(
                    registro['temperatura'],
                    registro['humedad'],
                    registro['viento']
                )
                
                if alertas:
                    hay_alertas = True
                    alertas_encontradas.append({
                        'zona': registro['distrito'],
                        'fecha': fecha,
                        'alertas': alertas
                    })
        
        # Mostrar alertas encontradas
        if alertas_encontradas:
            for item in alertas_encontradas:
                print(f"\n📍 ZONA: {item['zona']} | FECHA: {item['fecha']}")
                print("-" * 45)
                for alerta in item['alertas']:
                    print(f"  → {alerta}")
        else:
            print("\n✅ No hay alertas activas en ningún distrito.")
        
        print("\n" + "!"*66)
        if alertas_encontradas:
            total_alertas = sum(len(item['alertas']) for item in alertas_encontradas)
            print(f"Total de alertas activas: {total_alertas}")
        print("!"*66)
        
        input("\nPresione Enter para volver al menú...")
    
    def salir(self):
        """Cierre limpio del sistema"""
        self._mostrar_encabezado("🚪 CERRANDO SISTEMA")
        print("\n✅ Todos los datos han sido guardados correctamente")
        print("🌍 ¡Gracias por usar PyClima Resiliente!")
        print("👋 ¡Hasta pronto!\n")


def main():
    """Función principal para ejecutar la interfaz"""
    try:
        interfaz = InterfazPyClima("datos_clima.json")
        interfaz.menu_principal()
    except KeyboardInterrupt:
        print("\n\n❌ Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")


if __name__ == "__main__":
    main()
