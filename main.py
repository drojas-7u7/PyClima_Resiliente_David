"""
PyClima Resiliente - Sistema de Monitoreo Climático
DEV 4: Interfaz de Usuario + Sistema de Alertas

Interfaz de consola para registrar datos climáticos, consultar zonas
y visualizar históricos con alertas automáticas.
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Configurar UTF-8 para Windows
if os.name == 'nt':
    os.system('chcp 65001')

# Importar módulos del proyecto
import persistencia
from validaciones import (
    SistemaAlertas, 
    validar_input_numerico, 
    validar_input_si_no,
    validar_zona,
    mostrar_resumen_registro
)


class InterfazPyClima:
    """Controlador principal de la interfaz de usuario."""
    
    def __init__(self):
        self.sistema_alertas = SistemaAlertas()
        self.archivo_json = "datos_clima.json"
        self.archivo_config = "config.json"
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de la consola."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_encabezado(self, titulo: str = ""):
        """Muestra el encabezado del sistema."""
        self.limpiar_pantalla()
        print("\n" + "="*70)
        print("  🌦️  SISTEMA PYCLIMA RESILIENTE v1.0  ")
        print("  Sistema de Monitoreo Climático Avanzado")
        if titulo:
            print(f"  → {titulo}")
        print("="*70 + "\n")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal con todas las opciones."""
        self.mostrar_encabezado()
        
        print("📋 MENÚ PRINCIPAL\n")
        print("  1. 📝 Registrar Nuevos Datos Climáticos")
        print("  2. 🔍 Consultar Datos por Zona")
        print("  3. 📊 Ver Histórico Completo")
        print("  4. ⚠️  Ver Alertas Activas")
        print("  5. 🚪 Salir del Sistema")
        print("\n" + "-"*70)
    
    def obtener_opcion_menu(self) -> str:
        """Captura la opción del menú con validación."""
        while True:
            try:
                opcion = input("\nSeleccione una opción (1-5): ").strip()
                
                if opcion not in ['1', '2', '3', '4', '5']:
                    print("❌ ERROR: Seleccione una opción válida entre 1 y 5.")
                    continue
                
                return opcion
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupción del usuario. Saliendo...")
                sys.exit(0)
            except Exception as e:
                print(f"❌ ERROR: {e}")
    
    def registrar_datos_climáticos(self):
        """Flujo completo para registrar nuevos datos climáticos."""
        self.mostrar_encabezado("REGISTRAR NUEVOS DATOS")
        
        try:
            # Capturar fecha con validación
            print("1️⃣  FECHA DEL REGISTRO")
            while True:
                fecha_str = input("   Ingrese la fecha (DD/MM/AAAA): ").strip()
                
                try:
                    datetime.strptime(fecha_str, "%d/%m/%Y")
                    break
                except ValueError:
                    print("   ❌ Formato inválido. Use DD/MM/AAAA (ej: 25/03/2026)")
            
            # Capturar zona
            print("\n2️⃣  ZONA/DISTRITO")
            zona = ""
            while not zona:
                zona_input = input("   Nombre del distrito: ").strip()
                try:
                    zona = validar_zona(zona_input)
                except ValueError as e:
                    print(f"   ❌ ERROR: {e}")
            
            # Capturar temperatura
            print("\n3️⃣  PARÁMETROS CLIMÁTICOS")
            temperatura = validar_input_numerico(
                "   Temperatura (°C): ",
                tipo=float,
                rango=(-50, 60)
            )
            
            # Capturar humedad
            humedad = validar_input_numerico(
                "   Humedad relativa (%): ",
                tipo=float,
                rango=(0, 100)
            )
            
            # Capturar viento (opcional pero importante)
            viento = validar_input_numerico(
                "   Velocidad del viento (km/h): ",
                tipo=float,
                rango=(0, 200)
            )
            
            # Capturar lluvia
            print("   ¿Hay lluvia actualmente?")
            lluvia = validar_input_si_no("   Ingrese (S/N): ")
            
            # Construir registro
            registro = {
                "fecha": fecha_str,
                "distrito": zona,
                "temperatura": temperatura,
                "humedad": humedad,
                "viento": viento,
                "lluvia": lluvia,
                "timestamp": datetime.now().isoformat()
            }
            
            # Mostrar resumen
            mostrar_resumen_registro(registro)
            
            # ANÁLISIS DE ALERTAS ANTES DE GUARDAR
            print("🔍 ANALIZANDO CONDICIONES CLIMÁTICAS...\n")
            hay_alertas, mensajes_alerta = self.sistema_alertas.analizar_datos(registro)
            
            if hay_alertas:
                self.sistema_alertas.mostrar_alertas_visuales()
                
                print("⚠️  SE HAN DETECTADO CONDICIONES DE RIESGO")
                print("\n¿Desea continuar registrando estos datos?")
                
                if not validar_input_si_no("Ingrese (S/N): "):
                    print("\n✅ Operación cancelada pelo usuario. No se guardan los datos.")
                    input("\nPresione ENTER para continuar...")
                    return
            
            # Confirmación final antes de guardar
            print("\n" + "="*70)
            print("⚠️  CONFIRMACIÓN FINAL")
            print("="*70)
            confirmar = validar_input_si_no("¿Desea GUARDAR estos datos en el archivo? (S/N): ")
            
            if confirmar:
                exito = persistencia.registrar_nuevo_dato(registro)
                
                if exito:
                    print("\n✅ ¡Registro guardado exitosamente!")
                    print(f"   Zona: {zona}")
                    print(f"   Fecha: {fecha_str}")
                    print(f"   Temperatura: {temperatura}°C")
                else:
                    print("\n❌ No se pudo guardar el registro.")
            else:
                print("\n✅ Operación cancelada. No se guardaron los datos.")
            
            input("\nPresione ENTER para continuar...")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Operación cancelada por el usuario.")
            input("\nPresione ENTER para continuar...")
        except Exception as e:
            print(f"\n❌ ERROR INESPERADO: {e}")
            input("\nPresione ENTER para continuar...")
    
    def consultar_por_zona(self):
        """Consulta y filtra datos por zona específica."""
        self.mostrar_encabezado("CONSULTAR DATOS POR ZONA")
        
        try:
            # Obtener lista de distritos
            distritos = persistencia.obtener_distritos_permitidos()
            
            if not distritos:
                print("❌ No se pudieron cargar los distritos oficiales.")
                input("\nPresione ENTER para continuar...")
                return
            
            print("📍 DISTRITOS DISPONIBLES:\n")
            for i, distrito in enumerate(distritos, 1):
                print(f"   {i:2}. {distrito}")
            
            # Solicitar zona
            print("\n" + "-"*70)
            zona_buscada = input("\nIngrese el nombre del distrito a consultar: ").strip().title()
            
            if zona_buscada not in distritos:
                print(f"\n❌ ERROR: '{zona_buscada}' no es un distrito válido.")
                input("\nPresione ENTER para continuar...")
                return
            
            # Leer histórico y filtrar
            historico = persistencia.leer_historico()
            registros_zona = [r for r in historico if r.get("distrito", "").title() == zona_buscada]
            
            if not registros_zona:
                print(f"\n⚠️  No hay registros para el distrito '{zona_buscada}'.")
                input("\nPresione ENTER para continuar...")
                return
            
            # Mostrar registros
            print(f"\n📊 REGISTROS PARA {zona_buscada.upper()}")
            print("="*70)
            
            for i, registro in enumerate(registros_zona, 1):
                print(f"\n[Registro {i}]")
                print(f"  Fecha:        {registro.get('fecha', 'N/A')}")
                print(f"  Temperatura:  {registro.get('temperatura', 'N/A')}°C")
                print(f"  Humedad:      {registro.get('humedad', 'N/A')}%")
                print(f"  Viento:       {registro.get('viento', 'N/A')} km/h")
                print(f"  Lluvia:       {'Sí' if registro.get('lluvia') else 'No'}")
                print("-" * 70)
            
            print(f"\n✅ Total de registros encontrados: {len(registros_zona)}")
            
            input("\nPresione ENTER para continuar...")
        
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            input("\nPresione ENTER para continuar...")
    
    def ver_historico(self):
        """Muestra el histórico completo de registros."""
        self.mostrar_encabezado("VER HISTÓRICO COMPLETO")
        
        try:
            historico = persistencia.leer_historico()
            
            if not historico:
                print("⚠️  No hay registros en el histórico.")
                input("\nPresione ENTER para continuar...")
                return
            
            print(f"📊 HISTÓRICO COMPLETO ({len(historico)} registros)\n")
            print("="*70)
            
            for i, registro in enumerate(historico, 1):
                print(f"\n[Registro {i}/{len(historico)}]")
                print(f"  Fecha:        {registro.get('fecha', 'N/A')}")
                print(f"  Zona:         {registro.get('distrito', 'N/A')}")
                print(f"  Temperatura:  {registro.get('temperatura', 'N/A')}°C")
                print(f"  Humedad:      {registro.get('humedad', 'N/A')}%")
                print(f"  Viento:       {registro.get('viento', 'N/A')} km/h")
                print(f"  Lluvia:       {'Sí' if registro.get('lluvia') else 'No'}")
                print("-" * 70)
            
            print(f"\n✅ Total de registros: {len(historico)}")
            
            input("\nPresione ENTER para continuar...")
        
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            input("\nPresione ENTER para continuar...")
    
    def ver_alertas_activas(self):
        """Muestra información sobre el sistema de alertas."""
        self.mostrar_encabezado("INFORMACIÓN DE ALERTAS")
        
        print("⚠️  UMBRALES DE ALERTA DEL SISTEMA\n")
        print("="*70)
        print("\n  🔴 ALERTA CRÍTICA (Temperatura):")
        print("     • Nivel Crítico:   > 45°C")
        print("     • Nivel Alto:      > 40°C")
        print("\n  🔴 ALERTA CRÍTICA (Viento):")
        print("     • Nivel Crítico:   > 70 km/h")
        print("     • Nivel Alto:      > 50 km/h")
        print("\n  🟡 ALERTA (Lluvia/Humedad):")
        print("     • Lluvia Activa:   Detectada")
        print("     • Humedad Alta:    > 95%")
        print("     • Humedad Baja:    < 20%")
        print("\n" + "="*70)
        print("\n✅ Nota: Las alertas se generan automáticamente")
        print("   cuando registras datos climáticos.")
        
        input("\nPresione ENTER para continuar...")
    
    def salir_sistema(self):
        """Cierra el sistema con confirmación."""
        print("\n" + "="*70)
        print("🚪 SALIENDO DEL SISTEMA")
        print("="*70)
        
        print("\n¿Está seguro de que desea cerrar el sistema?")
        confirmar = validar_input_si_no("Ingrese (S/N): ")
        
        if confirmar:
            print("\n✅ Gracias por usar PyClima Resiliente. ¡Buen día!")
            print("   Sistema cerrado correctamente.\n")
            sys.exit(0)
        
        print("\n✅ Operación cancelada. Continuando...")
    
    def ejecutar(self):
        """Bucle principal de la aplicación."""
        while True:
            try:
                self.mostrar_menu_principal()
                opcion = self.obtener_opcion_menu()
                
                if opcion == "1":
                    self.registrar_datos_climáticos()
                elif opcion == "2":
                    self.consultar_por_zona()
                elif opcion == "3":
                    self.ver_historico()
                elif opcion == "4":
                    self.ver_alertas_activas()
                elif opcion == "5":
                    self.salir_sistema()
            
            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                input("\nPresione ENTER para continuar...")


def main():
    """Punto de entrada de la aplicación."""
    try:
        interfaz = InterfazPyClima()
        interfaz.ejecutar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Sistema interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()