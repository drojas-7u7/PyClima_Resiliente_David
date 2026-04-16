# PyClima Resiliente - Análisis Técnico Completo
## Guía Paso a Paso de Ejecución del Programa

**Responsable:** Equipo "Guardianes del Dato"  
**Tipo de Documento:** Especificación Técnica MVP  
**Audiencia:** Equipo de desarrollo, stakeholders técnicos

---

## 📋 TABLA DE CONTENIDOS
1. Arquitectura General
2. Flujo de Ejecución Paso a Paso
3. Sistema de Persistencia JSON
4. Validaciones Implementadas
5. Sistema de Alertas de Riesgo
6. Modelo de Datos

---

## 🏗️ ARQUITECTURA GENERAL

### Estructura Modular

```
PyClima_Resiliente/
├── main.py              → Punto de entrada y autenticación
├── interfaz.py          → Menú principal y operaciones
├── auth.py              → Gestión de usuarios/sesiones
├── persistencia.py      → Lectura/escritura JSON
├── validaciones.py      → Validación de entrada
├── alertas.py           → Evaluación de riesgos climáticos
├── analitica.py         → Generación de gráficos
├── config.json          → Configuración (umbrales, distritos)
├── datos_clima.json     → Base de datos histórica
├── usuarios.json        → Usuarios registrados
└── empleados.json       → Empleados autorizados
```

### Dependencias Principales
- `json` - Persistencia de datos
- `datetime` - Validación de fechas
- `difflib` - Corrección tipográfica en distritos
- `pwinput` - Entrada de contraseña enmascarada
- `matplotlib` / `seaborn` - Gráficos analíticos

---

## 🔄 FLUJO DE EJECUCIÓN PASO A PASO

### FASE 1: INICIALIZACIÓN DEL SISTEMA
```
[main.py: línea 14-20]
↓
┌─────────────────────────────────────────────────────────────┐
│ 1. Se imprime bandera bienvenida: "🌦️ SISTEMA PYCLIMA..."   │
│ 2. Se llama: persistencia.inicializar_archivo_datos()       │
│    - Si datos_clima.json NO existe → Se crea vacío []       │
│    - Si ya existe → Se ignora                               │
│ 3. Se establece: usuario_autenticado = None                 │
└─────────────────────────────────────────────────────────────┘
```

**Función responsable:** `persistencia.inicializar_archivo_datos()` (línea 100-107)
```python
# Si el archivo NO existe, lo crea vacío
if not os.path.exists(ARCHIVO_JSON):
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump([], f)  # Crea: [{"fecha": ..., "distrito": ...}, ...]
```

---

### FASE 2: EL MURO (BUCLE DE AUTENTICACIÓN)
```
[main.py: línea 26-47]
↓
┌──────────────────────────────────────────────────────────────┐
│ MIENTRAS usuario_autenticado = None:                         │
│                                                              │
│ Menú:                                                        │
│ ┌──────────────────────────────────────┐                   │
│ │ 1. Iniciar sesión                    │                   │
│ │ 2. Registrarse                       │                   │
│ │ 3. Cerrar programa                   │                   │
│ └──────────────────────────────────────┘                   │
│                                                              │
│ ├─ Opción "1" → auth.iniciar_sesion()                      │
│ │  └─ Retorna: {"num_empleado": "100375", "nombre": ...}  │
│ │  └─ Si es válido, rompe el bucle                        │
│ │                                                          │
│ ├─ Opción "2" → auth.registrar_usuario()                   │
│ │  └─ Vuelve al menú del Muro (no rompe bucle)           │
│ │                                                          │
│ └─ Opción "3" → exit() (cierra programa completamente)    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Funciones implicadas:**

**A) `auth.iniciar_sesion()` [auth.py: 133-161]**
```
1. Solicita num_empleado (máx 3 intentos contra usuarios.json)
   └─ validaciones.validar_usuario_sesion() [validaciones.py: 256-305]
   
2. Si num_empleado es válido:
   └─ Solicita contraseña (máx 3 intentos)
   └─ Compara contra usuarios.json[i]["password"]
   
3. Si coincide:
   └─ Retorna: u = {"nombre": "...", "apellidos": "...", "num_empleado": "..."}
   
4. Si falla:
   └─ Retorna: None (el bucle del Muro vuelve a empezar)
```

**B) `auth.registrar_usuario()` [auth.py: 82-131]**
```
Paso 1: Validar que sea empleado autorizado
  └─ validaciones.validar_acceso() contra empleados.json
  └─ Si NO existe en empleados.json → Cancela registro
  
Paso 2: Recopilar datos personales
  └─ Solicita: nombre, apellidos
  
Paso 3: Establecer contraseña
  └─ Valida: mínimo 8 caracteres alfanuméricos (sin símbolos)
  └─ Usa pwinput para enmascarar entrada
  
Paso 4: Guardar en usuarios.json
  └─ Append: {"nombre": "...", "apellidos": "...", 
              "num_empleado": "...", "password": "..."}
```

---

### FASE 3: ACCESO CONCEDIDO (MENÚ PRINCIPAL)
```
[main.py: 53-58] + [interfaz.py: 600-625]
↓
┌──────────────────────────────────────────────────────────────┐
│ Se instancia: app = InterfazPyClima(usuario_actual=...)     │
│              app.menu_principal()                            │
│                                                              │
│ MENÚ PRINCIPAL (bucle while True):                          │
│ ┌──────────────────────────────────────────┐               │
│ │ 1. 📋 Registrar Datos Climáticos         │               │
│ │ 2. 🔍 Consultar Datos                    │               │
│ │ 3. 📚 Ver Histórico (Todas las Zonas)    │               │
│ │ 4. 📢 Alertas Activas                    │               │
│ │ 5. 🔙 Salir                              │               │
│ └──────────────────────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📝 OPCIÓN 1: REGISTRAR DATOS CLIMÁTICOS

```
[interfaz.py: 87-163]
↓
┌─────────────────────────────────────────────────────────────┐
│ FLUJO DE REGISTRO DE DATOS:                                 │
│                                                             │
│ [1/6] Solicitar FECHA                                      │
│ └─ validaciones.validar_fecha()                            │
│    • Valida formato: AAAA-MM-DD                            │
│    • Rechaza fechas futuras                                │
│    • Retorna: string "2025-12-01"                          │
│                                                             │
│ [2/6] Solicitar ZONA/DISTRITO                              │
│ └─ validaciones.validar_zona()                             │
│    • Carga config.json → obtiene distritos_oficiales       │
│    • Normaliza entrada (ignora mayúsculas)                 │
│    • Sugiere correcciones tipográficas (difflib 60%)       │
│    • Retorna: "Retiro" (nombre oficial exacto)             │
│                                                             │
│ [VERIFICACIÓN] Comprobar duplicado                         │
│ └─ self._validar_duplicado(fecha, distrito)                │
│    • Itera sobre self.datos (lista cargada en RAM)        │
│    • Si existe registro con misma fecha + distrito → Error │
│    • Retorna: True (duplicado) o False (OK)                │
│                                                             │
│ [3/6] Solicitar TEMPERATURA                                │
│ └─ validaciones.validar_temperatura()                      │
│    • Rango: -20 a 50 °C                                    │
│    • Tipo: float (ej: 25.5)                                │
│    • Retorna valor validado                                │
│                                                             │
│ [4/6] Solicitar HUMEDAD                                    │
│ └─ validaciones.validar_humedad()                          │
│    • Rango: 0 a 100%                                       │
│    • Tipo: float (ej: 45.0)                                │
│                                                             │
│ [5/6] Solicitar VELOCIDAD DEL VIENTO                       │
│ └─ validaciones.validar_viento()                           │
│    • Rango: 0 a 150 km/h                                   │
│    • Tipo: float (ej: 12.5)                                │
│                                                             │
│ [6/6] Solicitar PRECIPITACIONES (LLUVIA)                   │
│ └─ validaciones.validar_lluvia()                           │
│    • Rango: 0 a 500 mm                                     │
│    • Tipo: float (ej: 15.5)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### EVALUACIÓN DE ALERTAS PRELIMINARES
```
[interfaz.py: 122-144]
↓
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: EVALUAR ALERTAS ANTES DE GUARDAR                    │
│                                                             │
│ umbrales = persistencia.obtener_umbrales_alerta()          │
│ datos_registro = {                                          │
│     "temperatura": 25.5,                                    │
│     "humedad": 45.0,                                        │
│     "viento": 12.5,                                         │
│     "lluvia": 0.0                                           │
│ }                                                           │
│                                                             │
│ alertas_activas = alertas.evaluar_alertas(datos_registro,  │
│                                           umbrales)         │
│ └─ Ver sección: SISTEMA DE ALERTAS                         │
│                                                             │
│ SI hay alertas:                                             │
│   🚨 ALERTAS PRELIMINARES DETECTADAS:                       │
│   → Muestra cada alerta con emoji y descripción             │
│                                                             │
│ SI NO hay alertas:                                          │
│   ✅ Niveles climáticos normales (Sin alertas)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### GUARDAR EN PERSISTENCIA
```
[interfaz.py: 136-150] + [persistencia.py: 47-89]
↓
┌─────────────────────────────────────────────────────────────┐
│ PASO 2: CONSTRUIR REGISTRO COMPLETO                         │
│                                                             │
│ nuevo_registro = {                                          │
│     "fecha": "2025-12-01",                                  │
│     "distrito": "Retiro",                                   │
│     "temperatura": 25.5,                          ← Clave  │
│     "temp": 25.5,              ← Clave alternativa (legacy) │
│     "humedad": 45.0,                                        │
│     "viento": 12.5,                                         │
│     "lluvia": 0.0,                                          │
│     "alertas": ["🔴 PELIGRO...", "🟠 RIESGO..."],          │
│     "registrado_por": "100375",        ← Usuario actual     │
│     "editado": False           ← Indicador de edición       │
│ }                                                           │
│                                                             │
│ exito = persistencia.registrar_nuevo_dato(nuevo_registro)  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**`persistencia.registrar_nuevo_dato()` [persistencia.py: 47-89]**
```python
# 1. Normalizar el distrito
distritos_oficiales = obtener_distritos_permitidos()  # De config.json
mapa_distritos = {d.lower(): d for d in distritos_oficiales}
distrito_limpio = mapa_distritos.get(distrito_ingresado.lower())

# 2. Validar que sea oficial
if distrito_limpio not in distritos_oficiales:
    print("❌ Error: No es un distrito oficial de Madrid")
    return False

# 3. VERIFICACIÓN CRÍTICA: Buscar duplicados
historico = leer_historico()  # Carga datos_clima.json
for entrada in historico:
    if entrada["fecha"] == nuevo_registro["fecha"]:
        if entrada["distrito"].lower() == distrito_limpio.lower():
            print("❌ Ya existe un registro para esta fecha/distrito")
            return False

# 4. Solicitar confirmación del usuario
print(f"Datos a registrar: {distrito_limpio} | {fecha} | {temperatura}°C")
confirmar = input("¿Confirmas guardar? (s/n): ")

# 5. SI CONFIRMA ('s'):
if confirmar == 's':
    nuevo_registro["distrito"] = distrito_limpio
    historico.append(nuevo_registro)  # Agregar a lista en RAM
    
    # 6. ESCRIBIR EN DISCO
    with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
        json.dump(historico, F, indent=4, ensure_ascii=False)
    print("✅ Registro guardado exitosamente")
    return True
```

---

## 🔍 OPCIÓN 2: CONSULTAR DATOS

```
[interfaz.py: 165-194]
↓
┌──────────────────────────────────────────────────────────┐
│ MENÚ DE CONSULTAS:                                       │
│ ┌────────────────────────────────────┐                 │
│ │ 1. Filtrar por Zona/Distrito       │                 │
│ │ 2. Filtrar por Fecha               │                 │
│ │ 3. Filtrar por Usuario             │                 │
│ │ 4. Volver al menú principal        │                 │
│ └────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────┘
```

### Submenú 1: Filtrar por Zona
```
[interfaz.py: 554-598]

1. Mostrar zonas disponibles (self.zonas_validas)
2. Usuario selecciona zona → self._ofrecer_grafica_zona(zona)
3. Opciones para zona seleccionada:
   • Ver datos tabulares
   • Generar gráfica de evolución térmica
   • Ver ambas
```

### Submenú 2: Filtrar por Fecha
```
[interfaz.py: 215-242]

1. Solicita fecha exacta: validaciones.validar_fecha()
2. Itera sobre self.datos
3. Busca: reg.get("fecha") == fecha_buscada
4. Para cada coincidencia, imprime:
   - 📍 Zona
   - 🌡️ Temperatura (usa reg.get('temp') O reg.get('temperatura'))
   - 💧 Humedad
   - 💨 Viento
   - Alertas asociadas (recalculadas)
```

### Submenú 3: Filtrar por Usuario (Mis registros/Editar)
```
[interfaz.py: 244-305]

1. Escanear self.datos → extraer "registrado_por"
2. Mostrar operarios con registros (usa auth.obtener_nombre_operario())
   └─ Resalta al usuario actual con "⬅️ (ESTE ERES TÚ)"
   
3. Usuario selecciona operario
4. Mostrar registros de ese operario:
   ├─ Si usuario_actual == operario seleccionado:
   │  └─ Ofrecer: "¿Desea editar uno de sus registros?"
   │     └─ if sí → self._editar_registro_usuario(registros_operario)
   │
   └─ Si usuario_actual ≠ operario seleccionado:
      └─ Mensaje: "ℹ️ Solo el usuario que registró puede editarlos"
```

**La edición está restringida:**
```
[interfaz.py: 307-377 + auth.py: 163-227]

RESTRICCIONES DE EDICIÓN:
1. Solo se puede editar UNA VEZ por registro
2. El usuario debe ser el creador (registrado_por == usuario_actual.num_empleado)
3. Si reg.get("editado") == True → BLOQUEADO

PROCESO DE EDICIÓN:
├─ Solicita confirmación explícita
├─ Pide nuevos valores con opción de mantener actuales
├─ Valida duplicados: no puede haber 2 registros mismo distrito/fecha
├─ Recalcula alertas con nuevos valores
├─ Marca como editado: reg["editado"] = True
└─ Guarda en disco: persistencia.actualizar_base_de_datos()
```

---

## 📚 OPCIÓN 3: VER HISTÓRICO COMPLETO

```
[interfaz.py: 403-474]
↓
┌───────────────────────────────────────────────────────┐
│ MENÚ HISTÓRICO:                                       │
│ ┌─────────────────────────────────────┐              │
│ │ 1. Ver histórico completo           │              │
│ │ 2. Ver gráfica del histórico         │              │
│ │ 3. Volver al menú principal          │              │
│ └─────────────────────────────────────┘              │
└───────────────────────────────────────────────────────┘
```

### Mostrar Histórico (Opción 1)
```
Para cada registro en self.datos:
├─ Imprime: 📅 Fecha | 📍 Distrito
├─ Imprime: 🌡️ T: XX°C | 💧 H: XX% | 💨 V: XX km/h
├─ Recalcula alertas (self._analizar_alertas)
├─ Imprime alertas activas (si las hay)
├─ Traduce ID operario a nombre completo (auth.obtener_nombre_operario)
├─ Si reg.get("editado") == True:
│  └─ Imprime: "⚠️ (Este registro ha sido editado/corregido)"
└─ Separador visual

Información de Autoría:
└─ Muestra: 👤 [Nombre Completo] (ID: num_empleado)
```

### Generar Gráfica (Opción 2)
```
[interfaz.py: 627-630] → [analitica.py: 10-80]

generar_reporte_visual_pro():
1. Carga datos_clima.json
2. Extrae pares (distrito, temperatura)
3. Filtra valores válidos (no None)
4. Genera gráfico de barras con matplotlib/seaborn:
   ├─ Eje X: Distritos
   ├─ Eje Y: Temperaturas
   ├─ Línea roja: Media general de temperaturas
   ├─ Línea azul punteada: Media de temperaturas bajo media
   └─ Línea naranja punteada: Media de temperaturas sobre media
```

---

## 🚨 OPCIÓN 4: PANEL DE ALERTAS ACTIVAS

```
[interfaz.py: 476-540]
↓
┌─────────────────────────────────────────────────────────┐
│ PANEL DE ALERTAS:                                       │
│                                                         │
│ 1. Recopila alertas actuales                            │
│    └─ Itera self.datos → recalcula alertas para c/uno   │
│       └─ Si alertas → agrega a alertas_encontradas      │
│                                                         │
│ 2. Si NO hay alertas:                                   │
│    └─ "✅ No hay alertas activas"                       │
│    └─ Vuelve a menú principal                           │
│                                                         │
│ 3. Si hay alertas:                                      │
│    └─ Muestra registro de alertas totales               │
│    └─ MENÚ DE OPCIONES:                                 │
│       ┌────────────────────────────────────┐           │
│       │ 1. Ver alertas de hoy              │           │
│       │ 2. Historial de alertas            │           │
│       │ 3. Filtrar por tipo de alerta      │           │
│       │ 4. Volver al menú principal        │           │
│       │ 5. Salir del sistema               │           │
│       └────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### SubFunciones del Panel

**1. Ver Alertas de Hoy**
```
[interfaz.py: 643-660]
fecha_hoy = datetime.now().strftime('%Y-%m-%d')
alertas_hoy = [item for item in lista_alertas if item['fecha'] == fecha_hoy]
```

**2. Historial de Alertas**
```
[interfaz.py: 633-641]
Imprime TODAS las alertas recopiladas con formato:
├─ 📍 ZONA | 📅 FECHA
├─ → [alerta 1]
├─ → [alerta 2]
└─ → [alerta N]
```

**3. Filtrar por Tipo de Alerta**
```
[interfaz.py: 662-726]

Palabras clave para clasificar:
{
    "Alerta de calor": ["calor", "temperatura elevada"],
    "Alerta de frío": ["frío", "helada", "frio"],
    "Alerta de viento": ["viento"],
    "Alerta de humedad": ["humedad", "sequedad"],
    "Alerta de lluvia": ["lluvia"]
}

Proceso:
1. Contar coincidencias de cada tipo
2. Mostrar menú dinámico: "Alerta de calor (5 detectadas)"
3. Usuario selecciona tipo
4. Filtrar y mostrar solo alertas de ese tipo
```

---

## 💾 SISTEMA DE PERSISTENCIA EN JSON

### Arquitectura de Lectura/Escritura

```
CAPA DE PERSISTENCIA [persistencia.py]
↓
┌──────────────────────────────────────────────────────────────┐
│ VARIABLES GLOBALES:                                          │
│ • ARCHIVO_JSON = "datos_clima.json"                          │
│ • CONFIGURACIÓN_DE_ARCHIVO = "config.json"                   │
│ • CONFIRMACIÓN_REQUERIDA = "si"                              │
└──────────────────────────────────────────────────────────────┘
```

### Funciones Principales

#### 1. `inicializar_archivo_datos()` [persistencia.py: 100-107]
```python
def inicializar_archivo_datos():
    """Crea datos_clima.json vacío si no existe"""
    if not os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump([], f)  # Inicializa como array vacío

# ESTRUCTURA INICIAL:
[]
```

#### 2. `leer_historico()` [persistencia.py: 33-45]
```python
def leer_historico():
    """Lee datos_clima.json completo en RAM"""
    if not os.path.exists(ARCHIVO_JSON):
        return []
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as F:
            return json.load(F)  # Carga lista completa en memoria
    except json.JSONDecodeError:
        # Si JSON corrupto → retorna [] (lista vacía)
        return []
    except Exception:
        return []

# LLAMADO POR:
# • interfaz.py: __init__() → self._cargar_datos()
# • interfaz.py: consultar_datos() → refrescar datos
# • persistencia.py: registrar_nuevo_dato()
```

#### 3. `registrar_nuevo_dato()` [persistencia.py: 47-89]
```
ENTRADA: nuevo_registro = {
    "fecha": "2025-12-01",
    "distrito": "Retiro",
    ...
}

PROCESO:
┌─ Paso 1: Normalizar distrito
│  └─ Usar mapa_distritos para obtener nombre oficial
│
├─ Paso 2: Validar contra distritos_oficiales
│  └─ Si NO está en lista → return False
│
├─ Paso 3: BUSCAR DUPLICADOS (crítico)
│  └─ historico = leer_historico()
│  └─ FOR cada entrada en historico:
│     IF entrada["fecha"] == nuevo_registro["fecha"] AND
│        entrada["distrito"].lower() == distrito.lower():
│        print("❌ Ya existe")
│        return False
│
├─ Paso 4: Pedir confirmación del usuario
│  └─ WHILE True:
│     confirmar = input("¿Confirmas? (s/n): ")
│     IF s → continuar
│     IF n → return False
│     ELSE → "No te he entendido"
│
└─ Paso 5: GUARDAR EN DISCO
   nuevo_registro["distrito"] = distrito_limpio
   historico.append(nuevo_registro)  # Agregar a lista
   with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
       json.dump(historico, F, indent=4, ensure_ascii=False)
   return True

SALIDA: True (éxito) | False (fallo)
```

#### 4. `actualizar_base_de_datos()` [persistencia.py: 91-98]
```python
def actualizar_base_de_datos(historico_modificado):
    """Sobrescribe datos_clima.json con nova lista"""
    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as F:
            json.dump(historico_modificado, F, indent=4, ensure_ascii=False)
        return True
    except Exception as mi:
        return False

# LLAMADO POR:
# • interfaz.py: _editar_registro_usuario() (después de editar)
# • auth.py: consultar_y_editar_historial()
```

#### 5. `obtener_distritos_permitidos()` [persistencia.py: 8-17]
```python
def obtener_distritos_permitidos():
    """Lee lista de distritos desde config.json"""
    if not os.path.exists(CONFIGURACIÓN_DE_ARCHIVO):
        return []
    try:
        with open(CONFIGURACIÓN_DE_ARCHIVO, 'r', encoding='utf-8') as F:
            config = json.load(F)
            return config.get("distritos_oficiales", [])
    except Exception:
        return []
```

#### 6. `obtener_umbrales_alerta()` [persistencia.py: 19-31]
```python
def obtener_umbrales_alerta():
    """Lee umbrales de alerta desde config.json"""
    if not os.path.exists(CONFIGURACIÓN_DE_ARCHIVO):
        return {}
    try:
        with open(CONFIGURACIÓN_DE_ARCHIVO, 'r', encoding='utf-8') as F:
            config = json.load(F)
            return config.get("umbrales", {})
    except Exception:
        return {}
```

### Modelo de Datos - Estructura de Registro

```json
{
    "fecha": "2025-12-01",                    // Formato: AAAA-MM-DD
    "distrito": "Retiro",                     // Debe estar en config.json
    "temperatura": 25.5,                      // Clave principal
    "temp": 25.5,                             // Clave alternativa (retrocompatibilidad)
    "humedad": 45.0,                          // Porcentaje 0-100%
    "viento": 12.5,                           // km/h
    "lluvia": 0.0,                            // mm
    "alertas": [                              // Array de strings
        "🔴 PELIGRO DE CALOR EXTREMO...",
        "🟠 RIESGO IMPORTANTE..."
    ],
    "registrado_por": "100375",               // ID del empleado (num_empleado)
    "editado": false                          // Indica si fue editado (True bloquea ediciones)
}
```

### Prevención de Duplicados

**Estrategia:**
```python
# 1. Todas las búsquedas usan combinación: fecha + distrito
# 2. Las búsquedas son case-insensitive para distrito
# 3. La búsqueda ocurre ANTES de solicitar confirmación

def _validar_duplicado(fecha, distrito):
    """En interfaz.py: 35-40"""
    for reg in self.datos:  # self.datos está en RAM
        if reg.get("fecha") == str(fecha) and \
           reg.get("distrito", "").lower() == distrito.lower():
            return True  # Hay duplicado
    return False  # Sin duplicado
```

---

## ✅ VALIDACIONES IMPLEMENTADAS

### 1. VALIDACIÓN DE FECHA

**Función:** `validaciones.validar_fecha()` [validaciones.py: 94-124]

```python
def validar_fecha():
    # FORMATO: AAAA-MM-DD
    # RANGO: Pasado o presente (NO futuro)
    
    VALIDACIONES:
    ├─ Vacío → ❌ "La fecha no puede estar vacía"
    ├─ Formato incorrecto → ❌ "Usa AAAA-MM-DD"
    ├─ Fecha inexistente → ❌ (ej: 2025-13-45)
    └─ Fecha futura → ❌ "No se permiten fechas futuras"
    
    RETORNA: string "2025-12-01"
    CANCELABLE: Escribir 'c'
```

**Ejemplo:**
```
Entrada: "2026-04-20" (fecha futura a partir de 2026-04-15)
Output: ❌ Error: No se permiten fechas futuras
        La fecha ingresada (2026-04-20) es posterior a hoy

Entrada: "2026-04-15" (hoy)
Output: ✅ Aceptado
```

---

### 2. VALIDACIÓN DE ZONA/DISTRITO

**Función:** `validaciones.validar_zona()` [validaciones.py: 127-184]

```python
def validar_zona():
    # CARGA: Lista de distritos desde config.json
    # NORMALIZACIÓN: Case-insensitive
    # CORRECCIÓN: Sugerencias automáticas si hay error tipográfico
    
    VALIDACIONES:
    ├─ Vacío → ❌ "La zona no puede estar vacía"
    ├─ No existe exacto → Busca sugerencias (difflib.get_close_matches)
    │  └─ Si encuentra coincidencia >60% similitud:
    │     └─ Pregunta: "¿Querías decir 'Retiro'?"
    │        • Si 's' → acepta sugerencia
    │        • Si 'n' → vuelve a solicitar
    └─ No hay sugerencias → ❌ "No coincide con ningún distrito"
    
    RETORNA: string "Retiro" (nombre oficial exacto)
    CANCELABLE: Escribir 'c'
```

**Ejemplo con corrección tipográfica:**
```
Entrada: "Retiro"
Output: ✅ "Retiro"

Entrada: "retiro" (minúsculas)
Output: ✅ "Retiro" (normalizado)

Entrada: "Retyro" (error tipográfico)
Output: 🤔 ¿Querías decir 'Retiro'? (s/n): s
Output: ✅ "Retiro"

Entrada: "XYZland" (no existe)
Output: ❌ "'XYZland' no coincide con ningún distrito oficial"
```

---

### 3. VALIDACIÓN DE TEMPERATURA

**Función:** `validaciones.validar_temperatura()` [validaciones.py: 16-39]

```python
RANGO: -20 a 50 °C
TIPO: float
VALIDACIONES:
├─ No numérico → ❌ "Introduce un número válido"
├─ Menor -20 → ❌ "Está fuera del rango permitido (-20 a 50)"
└─ Mayor 50 → ❌ "Está fuera del rango permitido (-20 a 50)"

RETORNA: float (ej: 25.5)
CANCELABLE: Escribir 'c'
```

---

### 4. VALIDACIÓN DE HUMEDAD

**Función:** `validaciones.validar_humedad()` [validaciones.py: 42-65]

```python
RANGO: 0 a 100%
TIPO: float
VALIDACIONES:
├─ No numérico → ❌ "Introduce un valor numérico"
├─ Menor 0 → ❌ "No es una humedad lógica (0 a 100)"
└─ Mayor 100 → ❌ "No es una humedad lógica (0 a 100)"

RETORNA: float (ej: 45.0)
CANCELABLE: Escribir 'c'
```

---

### 5. VALIDACIÓN DE VIENTO

**Función:** `validaciones.validar_viento()` [validaciones.py: 68-91]

```python
RANGO: 0 a 150 km/h
TIPO: float
VALIDACIONES:
├─ No numérico → ❌ "Debe ser un valor numérico"
├─ Menor 0 → ❌ "Está fuera del rango lógico (0 a 150)"
└─ Mayor 150 → ❌ "Está fuera del rango lógico (0 a 150)"

RETORNA: float (ej: 12.5)
CANCELABLE: Escribir 'c'

CONTEXTO: Velocidad de viento peligrosa se considera >= 40 km/h
```

---

### 6. VALIDACIÓN DE LLUVIA

**Función:** `validaciones.validar_lluvia()` [validaciones.py: 307-331]

```python
RANGO: 0 a 500 mm
TIPO: float
VALIDACIONES:
├─ No numérico → ❌ "Debe ser un valor numérico"
├─ Menor 0 → ❌ "Está fuera del rango lógico (0 a 500)"
└─ Mayor 500 → ❌ "Está fuera del rango lógico (0 a 500)"

RETORNA: float (ej: 15.5)
CANCELABLE: Escribir 'c'

UMBRAL TORRENCIAL: >= 50 mm → Alerta Roja
UMBRAL IMPORTANTE: 20-49 mm → Alerta Naranja
```

---

### 7. VALIDACIÓN DE NÚMERO DE EMPLEADO (Registro)

**Función:** `validaciones.validar_acceso()` [validaciones.py: 186-237]

```python
ARCHIVO FUENTE: empleados.json
MAX INTENTOS: 3
BÚSQUEDA: Exacta (string matching)

VALIDACIONES:
├─ Vacío → ❌ "No puede estar vacío"
├─ No existe en empleados.json → ❌ "NO reconocido" (intento +1)
└─ Agotados 3 intentos → ❌ "Has agotado los intentos"

UTILIDAD:
└─ Solo para REGISTRAR USUARIO (auth.registrar_usuario)
└─ Garantiza que solo empleados autorizados se registren

RETORNA: string "100375" (num_empleado)
CANCELABLE: Escribir 'c'
```

---

### 8. VALIDACIÓN DE NÚMERO DE EMPLEADO (Login)

**Función:** `validaciones.validar_usuario_sesion()` [validaciones.py: 256-305]

```python
ARCHIVO FUENTE: usuarios.json
MAX INTENTOS: 3
BÚSQUEDA: Exacta contra usuarios.json[i]["num_empleado"]

VALIDACIONES:
├─ Vacío → ❌ "No puede estar vacío"
├─ No existe en usuarios.json → ❌ "No está registrado" (intento +1)
└─ Agotados 3 intentos → ❌ "Has agotado los intentos"

UTILIDAD:
└─ Para INICIAR SESIÓN (auth.iniciar_sesion)
└─ Verifica que el usuario exista en la base de usuarios

RETORNA: string "100375" (num_empleado)
CANCELABLE: Escribir 'c'
```

---

### 9. VALIDACIÓN DE CONTRASEÑA

**Función:** En `auth.iniciar_sesion()` + `auth.registrar_usuario()`

```python
# REGISTRO:
REQUISITOS:
├─ Mínimo 8 caracteres
├─ Solo caracteres alfanuméricos (sin símbolos)
└─ Entrada enmascarada con pwinput (muestra **** en lugar de texto)

# LOGIN:
MAX INTENTOS: 3
BÚSQUEDA: Coincidencia exacta contra usuarios.json[i]["password"]
NOTA: Las contraseñas se guardan como plain text (NO HASHEADAS)
      ⚠️ RIESGO DE SEGURIDAD en producción (debería usarse bcrypt)
```

---

## 🚨 SISTEMA DE ALERTAS DE RIESGO

### Configuración de Umbrales [config.json]

```json
{
    "umbrales": {
        "temp_max_naranja": 35.0,      // Alerta naranja por calor
        "temp_max_roja": 40.0,          // Alerta roja por calor extremo
        "temp_min_alerta": 2.0,         // Alerta naranja por frío
        "temp_min_emergencia": -2.0,    // Alerta roja por helada extrema
        "viento_max": 40,               // Alerta naranja por viento
        "lluvia_naranja": 20.0,         // Alerta naranja por lluvia
        "lluvia_roja": 50.0,            // Alerta roja por lluvia torrencial
        "humedad_min": 15               // Alerta roja por sequedad
    }
}
```

### Función de Evaluación [alertas.py: 1-39]

```python
def evaluar_alertas(datos_registro, umbrales):
    """
    ENTRADA:
    - datos_registro: {"temperatura": 25.5, "humedad": 45, "viento": 12, "lluvia": 0}
    - umbrales: {"temp_max_roja": 40.0, ...}
    
    SALIDA:
    - alertas_activas: lista de strings ["🔴 PELIGRO...", "🟠 RIESGO..."]
    """
    
    alertas_activas = []
    
    # 1. EXTRAER VALORES (con conversión a float)
    temp = float(datos_registro.get("temperatura", 0))
    viento = float(datos_registro.get("viento", 0))
    humedad = float(datos_registro.get("humedad", 0))
    lluvia = float(datos_registro.get("lluvia", 0))
    
    # 2. EXTRAER UMBRALES
    t_roja = umbrales.get("temp_max_roja", 40.0)
    t_naranja = umbrales.get("temp_max_naranja", 35.0)
    t_alerta_frio = umbrales.get("temp_min_alerta", 2.0)
    t_emergencia_frio = umbrales.get("temp_min_emergencia", -2.0)
    v_max = umbrales.get("viento_max", 40)
    h_min = umbrales.get("humedad_min", 15)
    ll_naranja = umbrales.get("lluvia_naranja", 20.0)
    ll_roja = umbrales.get("lluvia_roja", 50.0)
    
    return alertas_activas
```

---

### TIPO 1: ALERTAS DE CALOR

```python
# ALERTA NARANJA (Temperatura elevada)
if temp >= t_naranja:  # >= 35°C
    alertas_activas.append(
        f"🟠 RIESGO IMPORTANTE: Alerta Naranja. 
           Temperatura elevada ({temp}°C)."
    )

# ALERTA ROJA (Calor extremo)
if temp >= t_roja:  # >= 40°C
    alertas_activas.append(
        f"🔴 PELIGRO DE CALOR EXTREMO: Alerta Roja. 
           Ola de calor ({temp}°C)."
    )

PRIORIDAD: Roja > Naranja
ACCIÓN REQUERIDA: Avisar a ciudadanos sobre hidratación, no salir
```

---

### TIPO 2: ALERTAS DE FRÍO

```python
# ALERTA NARANJA (Riesgo de helada)
if temp <= t_alerta_frio:  # <= 2°C
    alertas_activas.append(
        f"🟠 RIESGO IMPORTANTE: Riesgo de helada preventiva ({temp}°C)."
    )

# ALERTA ROJA (Helada extrema)
if temp <= t_emergencia_frio:  # <= -5°C
    alertas_activas.append(
        f"🔴 PELIGRO DE HELADA: Alerta Roja. 
           Frío extremo ({temp}°C). Riesgo infraestructuras."
    )

PRIORIDAD: Roja > Naranja
ACCIÓN REQUERIDA: Proteger tuberías, verificar infraestructura
```

---

### TIPO 3: ALERTAS DE VIENTO

```python
# ALERTA NARANJA (Viento peligroso)
if viento >= v_max:  # >= 40 km/h
    alertas_activas.append(
        f"🟠 VIENTO: Rachas de {viento} km/h. 
           Riesgo en parques."
    )

PRIORIDAD: Solo naranja (no hay roja para viento)
ACCIÓN REQUERIDA: Cerrar parques, avisar sobre caídas de objetos
```

---

### TIPO 4: ALERTAS DE LLUVIA

```python
# ALERTA NARANJA (Lluvia intensa)
if lluvia >= ll_naranja:  # >= 20 mm
    alertas_activas.append(
        f"🟠 RIESGO IMPORTANTE: Alerta Naranja. 
           Lluvia intensa ({lluvia} mm)."
    )

# ALERTA ROJA (Lluvia torrencial)
if lluvia >= ll_roja:  # >= 50 mm
    alertas_activas.append(
        f"🔴 PELIGRO DE LLUVIA TORRENCIAL: Alerta Roja. 
           Tormenta ({lluvia} mm)."
    )

PRIORIDAD: Roja > Naranja
ACCIÓN REQUERIDA: Alertas de inundación, cerrar zonas bajas
```

---

### TIPO 5: ALERTAS DE SEQUEDAD

```python
# ALERTA ROJA (Humedad crítica - riesgo de incendio)
if humedad <= h_min:  # <= 15%
    alertas_activas.append(
        f"🔴 RIESGO MUY ALTO: Humedad muy baja ({humedad}%). 
           Peligro de incendio."
    )

PRIORIDAD: Solo roja
ACCIÓN REQUERIDA: Prohibir hogueras, máxima alerta en bosques
```

---

### Flujo de Evaluación de Alertas (Pseudocódigo)

```python
def evaluar_alertas(datos_registro, umbrales):
    alertas_activas = []
    
    # Extraer valores
    temp = float(datos_registro.get("temperatura", 0))
    humedad = float(datos_registro.get("humedad", 0))
    viento = float(datos_registro.get("viento", 0))
    lluvia = float(datos_registro.get("lluvia", 0))
    
    # Extraer umbrales
    t_roja = umbrales.get("temp_max_roja", 40.0)
    t_naranja = umbrales.get("temp_max_naranja", 35.0)
    t_alerta_frio = umbrales.get("temp_min_alerta", 2.0)
    t_emergencia_frio = umbrales.get("temp_min_critica", -5.0)
    v_max = umbrales.get("viento_max", 40)
    h_min = umbrales.get("humedad_min", 15)
    ll_naranja = umbrales.get("lluvia_naranja", 20.0)
    ll_roja = umbrales.get("lluvia_roja", 50.0)
    
    # EVALUACIONES
    if temp >= t_roja:
        alertas_activas.append("🔴 CALOR EXTREMO")
    elif temp >= t_naranja:
        alertas_activas.append("🟠 CALOR ELEVADO")
    
    if temp <= t_emergencia_frio:
        alertas_activas.append("🔴 HELADA EXTREMA")
    elif temp <= t_alerta_frio:
        alertas_activas.append("🟠 RIESGO HELADA")
    
    if viento >= v_max:
        alertas_activas.append("🟠 VIENTO PELIGROSO")
    
    if lluvia >= ll_roja:
        alertas_activas.append("🔴 LLUVIA TORRENCIAL")
    elif lluvia >= ll_naranja:
        alertas_activas.append("🟠 LLUVIA INTENSA")
    
    if humedad <= h_min:
        alertas_activas.append("🔴 SEQUEDAD CRÍTICA")
    
    return alertas_activas
```

---

### Puntos de Evaluación de Alertas en la App

```
1. DURANTE REGISTRO DE DATOS
   └─ Se cacular ANTES de guardar
   └─ Se muestra para confirmar peligros
   └─ Se incluye en el registro guardado

2. DURANTE CONSULTAS
   └─ Se recalculan sobre-la-marcha
   └─ Se muestran en secciones de detalles
   └─ Se usan para el panel de alertas dinámico

3. DURANTE PANEL DE ALERTAS
   └─ Se recopilan todas las actuales
   └─ Se permiten filtros por tipo
   └─ Se muestran alertas "de hoy"
```

---

## 🔐 SEGURIDAD Y CONSIDERACIONES

### Fortalezas Implementadas ✅
1. **Validación exhaustiva** - Todos los inputs se validan antes de usar
2. **Prevención de duplicados** - Búsquedas fecha+distrito sin fallos
3. **Trazabilidad** - Todos los registros incluyen quién los creó
4. **Auditoría de ediciones** - Marca si un registro fue modificado
5. **Restricción de ediciones** - Solo se edita UNA VEZ
6. **Manejo de errores** - Try/except en lectura de archivos
7. **Normalización de datos** - Case-insensitive para distritos
8. **Autoría verificable** - auth.obtener_nombre_operario()

### Vulnerabilidades Identificadas ⚠️
1. **Contraseñas sin hash** - Plain text en usuarios.json (usar bcrypt)
2. **Sin cifrado** - JSON accesible directamente (considerar encryption)
3. **Sin logs** - No hay registro de acciones administrativas
4. **Sin permisos** - Falta control de roles (admin vs operario)
5. **Sin backup automático** - Sin respaldo ante corrupción

---

## 📊 ESTRUCTURA DE FLUJO VISUAL

```
┌───────────────┐
│  main.py      │ Punto de entrada
└───────┬───────┘
        │
        ├─► persistencia.inicializar_archivo_datos()
        │
        ├─► BUCLE MURO (while not usuario_autenticado):
        │   ├─► auth.iniciar_sesion() ─→ usuarios.json
        │   ├─► auth.registrar_usuario() ─→ usuarios.json
        │   └─► exit()
        │
        └─► InterfazPyClima(usuario_actual)
            │
            ├─► menu_principal()
            │   ├─► registrar_datos()
            │   │   ├─► validaciones.validar_*()
            │   │   ├─► alertas.evaluar_alertas()
            │   │   └─► persistencia.registrar_nuevo_dato()
            │   │
            │   ├─► consultar_datos()
            │   │   ├─► _menu_consultar_zona()
            │   │   ├─► _menu_consultar_fecha()
            │   │   ├─► _menu_consultar_usuario()
            │   │   └─► _editar_registro_usuario()
            │   │
            │   ├─► ver_historico()
            │   │   ├─► Mostrar todos los registros
            │   │   └─► generar_reporte_visual_pro() → analitica.py
            │   │
            │   ├─► mostrar_panel_alertas()
            │   │   ├─► _mostrar_alertas_hoy()
            │   │   ├─► _imprimir_alertas()
            │   │   └─► _filtrar_y_mostrar_alertas()
            │   │
            │   └─► salir() + exit()
            │
            └─► persistencia: datos_clima.json (lectura/escritura)
                └─► config.json (umbrales, distritos)
```

---

## 📝 RESUMEN EJECUTIVO

PyClima Resiliente es un **sistema de monitoreo climático de terminal** desarrollado bajo arquitectura modular con **5 capas funcionales**:

1. **Autenticación** (auth.py) - Control de acceso por empleado
2. **Entrada de Datos** (validaciones.py) - Validación exhaustiva de inputs
3. **Almacenamiento** (persistencia.py) - Persistencia JSON con control de duplicados
4. **Procesamiento** (alertas.py) - Evaluación de umbrales de riesgo
5. **Presentación** (interfaz.py + analitica.py) - Menús interactivos y reportes

**Capacidades principales:**
- ✅ Registrar datos climáticos por distrito con prevención de duplicados
- ✅ Consultar datos históricos con múltiples criterios de filtrado
- ✅ Generar alertas automáticas según 5 categorías de riesgo
- ✅ Visualizar tendencias con gráficos interactivos por distrito
- ✅ Editar registros propios (una única vez) con trazabilidad
- ✅ Historial de autoría completo para auditoría

**Datos guardados:** Más de 100 registros climáticos en datos_clima.json con información de todos los 21 distritos de Madrid.

