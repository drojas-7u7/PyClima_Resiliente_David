"""
Punto de Entrada - PyClima Resiliente
Responsable: Equipo "Guardianes del Dato"
Descripción: Archivo principal que arranca la interfaz del usuario.
"""

from interfaz import InterfazPyClima
import auth  # imporamos el modulo auth para que nos pida el usuario y contraseña
import persistencia

if __name__ == "__main__":
    try:
        # 1. Mensaje de bienvenida oficial del esquema
        print("\n" + "="*50)
        print("🌦️  SISTEMA PYCLIMA RESILIENTE")
        print("Sistema de Monitoreo Climático Avanzado")
        print("="*50)

        # INICIALIZACIÓN DEL SISTEMA (Punto 1 del esquema)
        persistencia.inicializar_archivo_datos()

        # 2. Creamos una variable vacía. Mientras esté vacía, el muro estará cerrado.
        usuario_autenticado = None

        # 3. EL BUCLE DE BIENVENIDA (El "Muro")
        while not usuario_autenticado:
            print("\n1. Iniciar sesión")
            print("2. Registrarse")
            print("3. Cerrar programa")
            
            opcion_inicio = input("Seleccione una opción (1-3): ").strip()

            if opcion_inicio == "1":
                # Llama a la función de auth.py. Si acierta, guardará los datos del usuario.
                # Si falla, devolverá None y el bucle volverá a empezar.
                usuario_autenticado = auth.iniciar_sesion()
                
            elif opcion_inicio == "2":
                # Llama al registro. El esquema dice que tras registrarse, vuelve al inicio.
                auth.registrar_usuario()
                
            elif opcion_inicio == "3":
                print("\nSaliendo del sistema de seguridad...")
                exit() # Esto apaga el programa por completo
                
            else:
                print("❌ Opción no válida. Intente de nuevo.")

        # ---------------------------------------------------------
        # 4. LA PUERTA SE ABRE
        # Si el programa llega a esta línea, significa que el bucle while terminó.
        # Y solo puede terminar si 'usuario_autenticado' tiene los datos correctos.
        print(f"\n✅ Acceso concedido.")
        
        # Instanciamos la interfaz y le pasamos los datos del operario
        app = InterfazPyClima(usuario_actual=usuario_autenticado)
        # Arrancamos el menú principal
        app.menu_principal()

    except KeyboardInterrupt:
        print("\n\n❌ Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico de inicio: {e}")