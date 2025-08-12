# Sistema de Análisis Biomecánico de Saltos - Prueba

## Descripción del Proyecto
EL presente tiene como objetivo generar una prueba de ensayo para su uso, de forma anticipada utiliza la cámara del computador para enlazar inicialmente una entrada de información dede el PC y así interpretar la información que captura.

Este cuenta con 2 etapas:
- Detección y escritura de landmarks sobre sujeto de prueba, adicional de pasos para exportar esta data de información a csv para su posterior análisis con el segundo código **[Archivo Principal]('Prototipo_prueba_mediapipe/Analisis_post_process.py')**.

## Características Principales

- **Detección de poses en tiempo real** usando MediaPipe (33 puntos clave)
- **Análisis biomecánico automatizado** (altura, tiempo de vuelo, ángulos articulares)
- **Detección automática de fases del salto** (despegue, vuelo, aterrizaje)
- **Cálculo de simetría bilateral** para evaluación técnica
- **Clasificación automática del tipo de salto**
- **Generación de reportes visuales** completos
- **Exportación de datos** en formato CSV
- **Comparación entre múltiples sesiones**
- **Interfaz de usuario** con entorno para iniciar la ejecución y finalizar por cada deportista evaluado

## Requisitos Previos

### Hardware Mínimo
- **CPU**: Intel i5 o AMD equivalente (recomendado: i7)
- **RAM**: 8 GB (recomendado: 16 GB)
- **Cámara web**: Resolución mínima 720p, 30 fps
- **Sistema operativo**: Windows 10/11, macOS 10.15+, o Linux Ubuntu 18.04+

### Software
- **Python 3.8 o superior**
- **Pip** (gestor de paquetes de Python)

## Instalación

### Paso 1: Clonar o descargar los archivos
```bash
# Utiliza nuestro repo y clona el archivo principal con el entorno simulado
git clone <repository-url>
cd jump-analysis-system

# O descarga los archivos manualmente y extrae en una carpeta
```

### Paso 2: Ejecutar configuración automática
```bash
# Ejecuta el script de configuración
python setup_environment.py
```

Este script:
- ✅ Verifica la compatibilidad del sistema
- ✅ Instala todas las dependencias necesarias
- ✅ Verifica el funcionamiento de la cámara
- ✅ Crea la estructura de carpetas del proyecto

### Paso 3: Instalación manual (si es necesario)
```bash
# Instalar dependencias manualmente
pip install opencv-python>=4.8.0
pip install mediapipe>=0.10.0
pip install numpy>=1.21.0
pip install pandas>=1.3.0
pip install matplotlib>=3.5.0
pip install seaborn>=0.11.0
pip install scipy>=1.7.0
pip install scikit-learn>=1.0.0
```

## Uso del Sistema

### Captura de Datos en Tiempo Real

```bash
python jump_analysis_prototype.py
```

**Controles durante la captura:**
- `Iniciar/detener grabación`
- `Guardar datos de la sesión actual`
- `Salir del programa`

**Instrucciones para mejores resultados:**
1. Colócate de **perfil** a la cámara (vista lateral)
2. Mantén una distancia de **2-3 metros** de la cámara
3. Asegúrate de tener **buena iluminación**
4. Usa ropa **contrastante** con el fondo
5. Realiza movimientos **fluidos y naturales**

### Análisis Post-Procesamiento

```bash
python data_analysis_script.py
```

Este script automáticamente:
- Encuentra el archivo de datos más reciente
- Calcula métricas biomecánicas avanzadas
- Clasifica el tipo de salto realizado
- Genera reportes visuales completos
- Exporta resúmenes en CSV
- Proporciona recomendaciones técnicas

### Generar Datos de Demostración

```bash
python setup_requirements.py
```

Incluye un generador que crea datos sintéticos realistas para probar el sistema sin necesidad de realizar saltos reales.

## Métricas Calculadas

### Métricas Físicas
- **Altura de salto** (cm): Elevación máxima del centro de masa
- **Tiempo de vuelo** (s): Duración en el aire
- **Velocidad de despegue** (m/s): Velocidad vertical inicial
- **Potencia estimada** (W): Usando fórmulas de Sayers y física básica

### Métricas Técnicas
- **Ángulos articulares**: Rodilla, cadera y tobillo en despegue
- **Índice de simetría bilateral** (%): Equilibrio entre extremidades
- **Clasificación de técnica**: SJ, CMJ, DJ, etc.
- **Calidad del movimiento**: Evaluación de la ejecución técnica

### Métricas de Análisis Temporal
- **Detección de fases**: Preparación, despegue, vuelo, aterrizaje
- **Patrones de movimiento**: Secuencias de activación articular
- **Coordinación**: Sincronización entre segmentos corporales

## Estructura de Archivos

```
jump-analysis-system/
├── jump_analysis_prototype.py      # Sistema principal de captura
├── data_analysis_script.py         # Análisis post-procesamiento
├── setup_environment.py            # Configuración automática
├── requirements.txt                # Dependencias del proyecto
├── README.md                      # Este archivo
├── data/                          # Datos capturados
│   ├── jump_analysis_XXXXXX.csv   # Datos brutos de sesiones
│   └── jump_summary_XXXXXX.csv    # Resúmenes de métricas
├── reports/                       # Reportes generados
│   ├── jump_report_XXXXXX.png     # Análisis visual completo
│   └── jump_comparison_XXXXXX.png # Comparaciones entre sesiones
└── exports/                       # Exportaciones adicionales
    └── processed_data_XXXXXX.csv  # Datos procesados
```

## Casos de Uso

### 1. Evaluación Individual
```python
# Ejecutar captura
python jump_analysis_prototype.py
# Realizar 3-5 saltos con grabación activa
# Analizar resultados
python data_analysis_script.py
```

### 2. Seguimiento de Progreso
```python
# Realizar sesiones en diferentes fechas
# Comparar automáticamente múltiples archivos
# El sistema detecta mejoras o deterioros
```

### 3. Análisis Técnico Detallado
```python
# Revisar ángulos articulares específicos
# Identificar asimetrías o compensaciones
# Obtener recomendaciones de mejora
```

## Interpretación de Resultados

### Valores de Referencia (Deportistas Recreativos)

| Métrica | Principiante | Intermedio | Avanzado |
|---------|-------------|------------|----------|
| **Altura SJ** | 15-25 cm | 25-35 cm | 35-50+ cm |
| **Altura CMJ** | 18-28 cm | 28-40 cm | 40-60+ cm |
| **Tiempo vuelo** | 0.20-0.30 s | 0.30-0.40 s | 0.40-0.50+ s |
| **Simetría** | 70-85% | 85-92% | 92-98% |
| **Potencia** | 800-1500 W | 1500-2500 W | 2500-4000+ W |

### Indicadores de Técnica

** Técnica Excelente:**
- Simetría > 90%
- Ángulos de rodilla 90-120° en despegue
- Coordinación fluida de extremidades

** Técnica Moderada:**
- Simetría 80-90%
- Ligeras compensaciones detectables
- Margen de mejora identificado

** Técnica Deficiente:**
- Simetría < 80%
- Asimetrías significativas
- Patrones de riesgo de lesión

## Solución de Problemas

### Problemas Comunes

** "No se detecta la cámara"**
```bash
# Verificar dispositivos disponibles
python -c "import cv2; print(cv2.videoio_registry.getCameraBackends())"

# Probar diferentes índices de cámara
cap = cv2.VideoCapture(1)  # Probar 0, 1, 2...
```

**❌ "MediaPipe no detecta poses"**
- ✅ Verificar iluminación (mínimo 500 lux)
- ✅ Usar fondo contrastante
- ✅ Evitar ropa del mismo color que el fondo
- ✅ Mantener distancia adecuada (2-4 metros)

**❌ "Métricas inconsistentes"**
- ✅ Realizar calibración de 30 segundos antes del salto
- ✅ Mantener la cámara estable
- ✅ Evitar objetos en movimiento en el fondo

**❌ "Error al instalar dependencias"**
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar con versiones específicas
pip install opencv-python==4.8.1.78
pip install mediapipe==0.10.7
```

### Optimización de Rendimiento

**Para equipos con recursos limitados:**
```python
# Reducir resolución de cámara
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Reducir complejidad del modelo MediaPipe
pose = mp_pose.Pose(model_complexity=0)  # 0=ligero, 1=completo, 2=pesado
```

**Para equipos potentes:**
```python
# Aumentar resolución y FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 60)

# Usar modelo completo
pose = mp_pose.Pose(model_complexity=2)
```

##  Validación Científica

### Comparación con Gold Standard
Este prototipo está diseñado para validarse contra:
- **Plataformas de fuerza** (Kistler, AMTI)
- **Sistemas de captura 3D** (OptiTrack, Vicon)
- **Dispositivos comerciales** (Gyko, VERT)

### Precisión Esperada
- **Altura de salto**: ±3-5 cm vs plataforma de fuerza
- **Tiempo de vuelo**: ±0.02-0.05 s vs cronometraje profesional
- **Ángulos articulares**: ±5-8° vs goniometría manual

### Limitaciones Conocidas
- **Dependiente de iluminación**: Requiere condiciones controladas
- **Precisión absoluta**: Menor que sistemas profesionales (±10-15%)
- **2D vs 3D**: Análisis limitado al plano sagital/frontal
- **Calibración individual**: Requiere ajustes por sujeto

## Fundamento Científico

### Referencias Implementadas
1. **MediaPipe Pose**: Bazarevsky et al. (2020) - Google Research
2. **Ecuaciones biomecánicas**: Bosco et al. (1983), Winter (2009)
3. **Fórmulas de potencia**: Sayers et al. (1999), Johnson & Bahamonde (1996)
4. **Análisis de simetría**: Impellizzeri et al. (2007)

### Aplicaciones en Investigación
- **Análisis de rendimiento deportivo**
- **Evaluación de intervenciones de entrenamiento**
- **Detección de asimetrías y riesgo de lesión**
- **Seguimiento de rehabilitación**

## Contribuciones y Desarrollo

### Mejoras Futuras Planificadas
- [ ] **Integración con sensores IMU** reales
- [ ] **Análisis 3D** con múltiples cámaras
- [ ] **Machine Learning** para clasificación automática
- [ ] **Aplicación móvil** para análisis en campo
- [ ] **Base de datos** para seguimiento longitudinal

### Cómo Contribuir
1. Fork del repositorio
2. Crear branch para nuevas características
3. Implementar y probar cambios
4. Documentar modificaciones
5. Crear Pull Request

## 📞 Soporte y Contacto

### Para Problemas Técnicos
- 📧 Email: [danielan.ramirezs@ecci.edu.co]

### Para Colaboraciones Académicas
- Universidad ECCI - Facultad de Ingeniería
- Directores de Tesis: Ing. Ronald Rodriguez, Ing. Nataly Maldonado
- Bogotá D.C., Colombia

## Licencia

Este proyecto se desarrolla como parte de una tesis de grado en Ingeniería Electrónica y está disponible para uso académico y de investigación.

**Cita recomendada:**
```bibtex
@mastersthesis{ramirez_campo_lopez_2025jump,
  title={Metodología Híbrida Inercial-Visual para el Análisis Técnico y Físico del Salto largo en Deportistas},
  author={Ramírez, Daniel A. and Campo, José A. and López, Diego A.},
  school={Universidad ECCI},
  year={2025},
  address={Bogotá D.C., Colombia}
}
```

---

##  Comienza el análisis:

```bash
# Configuración inicial
python setup_environment.py

# Generar datos de prueba (opcional)
python setup_requirements.py

# Iniciar captura en tiempo real
python jump_analysis_prototype.py

# Analizar datos capturados
python data_analysis_script.py
```

**¡Esperamos que este sistema contribuya al desarrollo del deporte y la biomecánica en Colombia, evaluando el rendimiento de diferentes deportistas a nivel local y mundial, con el fin de contribuir en la mejora del modelo de estudio**
-

