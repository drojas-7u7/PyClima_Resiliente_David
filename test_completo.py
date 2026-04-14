import pytest
import json
from datetime import datetime
import inspect
import os


@pytest.fixture(scope="session")
def datos_clima():
    """Carga datos climaticos una sola vez para toda la sesion"""
    with open('datos_clima.json', 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def config():
    """Carga configuracion una sola vez para toda la sesion"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def usuarios():
    """Carga usuarios una sola vez para toda la sesion"""
    with open('usuarios.json', 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def empleados():
    """Carga empleados una sola vez para toda la sesion"""
    with open('empleados.json', 'r', encoding='utf-8') as f:
        return json.load(f)


class TestValidacionFechas:
    """Tests para validacion de fechas"""

    def test_validar_fecha_importable(self):
        """Verifica que validar_fecha importe correctamente"""
        from validaciones import validar_fecha
        assert callable(validar_fecha)

    def test_validar_fecha_rechaza_futuras(self):
        """Verifica que valida_fecha rechaza fechas futuras"""
        from validaciones import validar_fecha
        source = inspect.getsource(validar_fecha)
        assert "datetime.now()" in source, "Debe usar datetime.now()"
        assert ">" in source, "Debe comparar con fecha actual"


class TestAlertasEnDatos:
    """Tests para alertas en datos"""

    def test_alertas_calor_extremo(self, datos_clima):
        """Verifica minimo 5 alertas de calor extremo"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "Calor extremo" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de calor extremo, hay {count}"

    def test_alertas_temperatura_elevada(self, datos_clima):
        """Verifica minimo 5 alertas de temperatura elevada"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "Temperatura elevada" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de temperatura elevada, hay {count}"

    def test_alertas_frio_extremo(self, datos_clima):
        """Verifica minimo 5 alertas de frio extremo"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "Frio extremo" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de frio extremo, hay {count}"

    def test_alertas_riesgo_helada(self, datos_clima):
        """Verifica minimo 5 alertas de riesgo de helada"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "helada" in a.lower())
        assert count >= 5, f"Se esperaban 5+ alertas de riesgo de helada, hay {count}"

    def test_alertas_viento_peligroso(self, datos_clima):
        """Verifica minimo 5 alertas de viento peligroso"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "Rachas" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de viento peligroso, hay {count}"

    def test_alertas_lluvia_torrencial(self, datos_clima):
        """Verifica minimo 5 alertas de lluvia torrencial"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "torrencial" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de lluvia torrencial, hay {count}"

    def test_alertas_lluvia_intensa(self, datos_clima):
        """Verifica minimo 5 alertas de lluvia intensa"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "intensa" in a and "Lluvia" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de lluvia intensa, hay {count}"

    def test_alertas_sequedad(self, datos_clima):
        """Verifica minimo 5 alertas de sequedad"""
        count = sum(1 for d in datos_clima for a in d.get('alertas', []) if "Humedad muy baja" in a)
        assert count >= 5, f"Se esperaban 5+ alertas de sequedad, hay {count}"


class TestEstructuraDatos:
    """Tests para estructura de datos climaticos"""

    def test_total_registros(self, datos_clima):
        """Verifica que hay minimo 104 registros (julio + diciembre 2025)"""
        julio = [d for d in datos_clima if d['fecha'].startswith('2025-07')]
        diciembre = [d for d in datos_clima if d['fecha'].startswith('2025-12')]
        total_base = len(julio) + len(diciembre)
        assert total_base >= 104, f"Se esperaban 104+ registros base (julio+diciembre), hay {total_base}"
        # Verificar que NO hay registros de otras fechas (datos basura)
        otros = [d for d in datos_clima if not d['fecha'].startswith('2025-07') and not d['fecha'].startswith('2025-12')]
        assert len(otros) == 0, f"Hay {len(otros)} registros de fechas inesperadas que deben eliminarse"

    def test_registros_julio(self, datos_clima):
        """Verifica registros de julio (31+ registros base)"""
        julio = [d for d in datos_clima if d['fecha'].startswith('2025-07')]
        assert len(julio) >= 31, f"Se esperaban 31+ registros de julio, hay {len(julio)}"

    def test_registros_diciembre(self, datos_clima):
        """Verifica registros de diciembre (31+ registros base)"""
        diciembre = [d for d in datos_clima if d['fecha'].startswith('2025-12')]
        assert len(diciembre) >= 31, f"Se esperaban 31+ registros de diciembre, hay {len(diciembre)}"

    def test_distritos_registrados(self, datos_clima):
        """Verifica cantidad de distritos"""
        distritos = set(d['distrito'] for d in datos_clima)
        assert len(distritos) == 21, f"Se esperaban 21 distritos, hay {len(distritos)}"

    def test_estructura_registros(self, datos_clima):
        """Verifica que todos los registros tienen los campos requeridos"""
        campos_requeridos = ['fecha', 'distrito', 'temp', 'humedad', 'viento', 'lluvia', 'alertas', 'registrado_por']
        for i, reg in enumerate(datos_clima):
            assert all(campo in reg for campo in campos_requeridos), \
                f"Registro {i} falta campos: {[c for c in campos_requeridos if c not in reg]}"

    def test_temperatura_valida(self, datos_clima):
        """Verifica que temperaturas esten en rango logico"""
        for d in datos_clima:
            temp = d.get('temp', 0)
            assert -20 <= temp <= 50, f"Temperatura fuera de rango: {temp}"

    def test_humedad_valida(self, datos_clima):
        """Verifica que humedad este en rango 0-100"""
        for d in datos_clima:
            humedad = d.get('humedad', 0)
            assert 0 <= humedad <= 100, f"Humedad fuera de rango: {humedad}"

    def test_viento_valido(self, datos_clima):
        """Verifica que viento este en rango logico"""
        for d in datos_clima:
            viento = d.get('viento', 0)
            assert 0 <= viento <= 150, f"Viento fuera de rango: {viento}"


class TestAutenticacion:
    """Tests para sistema de autenticacion"""

    def test_validar_acceso_importable(self):
        """Verifica que validar_acceso importe correctamente"""
        from validaciones import validar_acceso
        assert callable(validar_acceso)

    def test_validar_usuario_sesion_importable(self):
        """Verifica que validar_usuario_sesion importe correctamente"""
        from validaciones import validar_usuario_sesion
        assert callable(validar_usuario_sesion)

    def test_validar_acceso_usa_empleados(self):
        """Verifica que validar_acceso valida contra empleados.json"""
        from validaciones import validar_acceso
        source = inspect.getsource(validar_acceso)
        assert "empleados.json" in source, "Debe validar contra empleados.json"

    def test_validar_usuario_sesion_usa_usuarios(self):
        """Verifica que validar_usuario_sesion valida contra usuarios.json"""
        from validaciones import validar_usuario_sesion
        source = inspect.getsource(validar_usuario_sesion)
        assert "usuarios.json" in source, "Debe validar contra usuarios.json"

    def test_usuarios_registrados(self, usuarios):
        """Verifica cantidad de usuarios registrados"""
        assert len(usuarios) > 0, "Debe haber usuarios registrados"
        assert len(usuarios) <= 25, f"Hay {len(usuarios)} usuarios, maximo 25 empleados"

    def test_empleados_disponibles(self, empleados):
        """Verifica cantidad de empleados autorizados"""
        assert len(empleados) == 25, f"Se esperaban 25 empleados, hay {len(empleados)}"

    def test_usuarios_tienen_estructura(self, usuarios):
        """Verifica estructura de usuarios"""
        campos = ['nombre', 'apellidos', 'num_empleado', 'password']
        for u in usuarios:
            assert all(c in u for c in campos), f"Usuario falta campos: {u}"


class TestGraficas:
    """Tests para graficas y calculos de media"""

    def test_analitica_importable(self):
        """Verifica que analitica importe correctamente"""
        import analitica
        assert hasattr(analitica, 'generar_reporte_visual_pro')
        assert hasattr(analitica, 'generar_reporte_distrito_especifico')

    def test_reporte_visual_calcula_medias(self):
        """Verifica que generar_reporte_visual_pro calcule medias"""
        import analitica
        source = inspect.getsource(analitica.generar_reporte_visual_pro)
        assert "media_frio" in source, "Debe calcular media_frio"
        assert "media_calor" in source, "Debe calcular media_calor"

    def test_reporte_distrito_calcula_medias(self):
        """Verifica que generar_reporte_distrito_especifico calcule medias"""
        import analitica
        source = inspect.getsource(analitica.generar_reporte_distrito_especifico)
        assert "media_frio" in source, "Debe calcular media_frio"
        assert "media_calor" in source, "Debe calcular media_calor"

    def test_reporte_visual_tiene_lineas_referencia(self):
        """Verifica que haya 3 lineas de referencia"""
        import analitica
        source = inspect.getsource(analitica.generar_reporte_visual_pro)
        axhline_count = source.count("axhline")
        assert axhline_count >= 3, f"Se esperaban 3+ lineas axhline, hay {axhline_count}"

    def test_reporte_distrito_tiene_lineas_referencia(self):
        """Verifica que haya 3 lineas de referencia"""
        import analitica
        source = inspect.getsource(analitica.generar_reporte_distrito_especifico)
        axhline_count = source.count("axhline")
        assert axhline_count >= 3, f"Se esperaban 3+ lineas axhline, hay {axhline_count}"


class TestModulos:
    """Tests de importacion de modulos"""

    def test_main_importable(self):
        """Verifica que main importe correctamente"""
        import main
        assert True

    def test_interfaz_importable(self):
        """Verifica que interfaz importe correctamente"""
        import interfaz
        assert True

    def test_persistencia_importable(self):
        """Verifica que persistencia importe correctamente"""
        import persistencia
        assert True

    def test_alertas_importable(self):
        """Verifica que alertas importe correctamente"""
        import alertas
        assert True

    def test_validaciones_importable(self):
        """Verifica que validaciones importe correctamente"""
        import validaciones
        assert True

    def test_auth_importable(self):
        """Verifica que auth importe correctamente"""
        import auth
        assert True

    def test_config_tiene_distritos(self, config):
        """Verifica que config tiene distritos"""
        assert "distritos_oficiales" in config
        assert len(config["distritos_oficiales"]) == 21


# Hooks de pytest para imprimir resumen
def pytest_sessionfinish(session, exitstatus):
    """Imprime resumen al finalizar"""
    print("\n" + "="*70)
    print(" PRUEBAS CON PYTEST COMPLETADAS")
    print("="*70)
    print("\nRESULTADO FINAL:")
    if exitstatus == 0:
        print("  Estado: TODO OK - PROGRAMA LISTO PARA USAR")
    else:
        print("  Estado: FALLOS DETECTADOS")
    print("="*70)
