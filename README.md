# Sistema Integral de Gestión Hospitalaria

Sistema web para la administración, análisis y visualización de datos hospitalarios, con autenticación por roles y módulos de Machine Learning orientados a la toma de decisiones.

---

## Descripción

El **Sistema Integral de Gestión Hospitalaria** permite administrar diferentes procesos relacionados con la operación de una institución hospitalaria.

El sistema permite gestionar:

* Pacientes
* Médicos
* Citas
* Consultas
* Diagnósticos
* Tratamientos
* Hospitalizaciones
* Pagos
* Usuarios y roles

Además, incorpora un **dashboard interactivo** con indicadores y gráficas, un módulo de **Machine Learning** para análisis predictivo y generación de informes en formatos **PDF y ODF**.

### Características principales

* Autenticación de usuarios mediante roles.
* Gestión de usuarios administrativos.
* Roles disponibles:

  * Administrador
  * Médico
  * Recepcionista
  * Enfermería
* CRUD completo para pacientes, médicos, citas, consultas, diagnósticos, tratamientos y hospitalizaciones.
* Dashboard con KPIs y gráficas interactivas.
* Visualización de:

  * Consultas por mes.
  * Demanda por especialidad.
  * Enfermedades frecuentes.
  * Ocupación hospitalaria.
  * Costos de atención.
  * Indicadores generales del hospital.
* Machine Learning para:

  * Clasificación.
  * Regresión.
  * Clustering.
* Predicción del riesgo de cancelación de citas.
* Predicción de demanda de consultas.
* Predicción de costos de atención.
* Agrupación de pacientes mediante clustering.
* Generación de informes PDF.
* Generación de informes ODF.
* Subida de fotografías de perfil.
* Base de datos MongoDB Atlas.
* Índices optimizados para mejorar el rendimiento de las consultas.

---

## Tecnologías utilizadas

| Tecnología    | Versión | Propósito                            |
| ------------- | ------: | ------------------------------------ |
| Python        |   3.11+ | Lenguaje de programación principal   |
| Flask         |   2.3.3 | Framework web para el backend        |
| MongoDB Atlas |       - | Base de datos NoSQL en la nube       |
| PyMongo       |   4.6.1 | Conector para MongoDB                |
| Pandas        |   2.1.4 | Manipulación y análisis de datos     |
| NumPy         |  1.26.3 | Operaciones numéricas                |
| Scikit-learn  |   1.4.0 | Machine Learning                     |
| Chart.js      |   3.9.1 | Visualización de gráficas            |
| html2pdf.js   |  0.10.1 | Generación de PDF desde el navegador |
| odfpy         |   1.4.1 | Generación de informes ODF           |

---

## Requisitos previos

Antes de instalar el proyecto se requiere:

* Python 3.11 o superior.
* MongoDB Atlas o una instalación local de MongoDB.
* Git.
* Pip.
* Navegador web moderno.

### Opcional

Para utilizar el sistema de generación de datos mediante inteligencia artificial:

* Cuenta de Google AI Studio.
* API Key de Gemini.

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
```

### 2. Crear un entorno virtual

#### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
MONGO_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>.mongodb.net/
DATABASE_NAME=hospital_artoria
SECRET_KEY=tu_clave_secreta_aqui
GEMINI_API_KEY=tu_clave_de_gemini
```

### Variables disponibles

| Variable         | Descripción                                |
| ---------------- | ------------------------------------------ |
| `MONGO_URI`      | Cadena de conexión de MongoDB Atlas        |
| `DATABASE_NAME`  | Nombre de la base de datos                 |
| `SECRET_KEY`     | Clave utilizada para las sesiones de Flask |
| `GEMINI_API_KEY` | API Key de Gemini para generación de datos |

> `GEMINI_API_KEY` es opcional y solamente es necesaria para las funciones de generación de datos mediante Gemini.

### Generar una SECRET_KEY

Puedes generar una clave segura utilizando Python:

```python
import os
print(os.urandom(24).hex())
```

---

## Inicialización de la base de datos

Para poblar la base de datos con información de prueba puedes ejecutar:

```bash
python seed_db.py --clean
```

El proceso intentará utilizar Gemini para generar los datos cuando exista una `GEMINI_API_KEY` configurada.

Si Gemini no está disponible, el sistema puede utilizar datos generados localmente como respaldo.

---

## Ejecutar la aplicación

Una vez configurado el proyecto:

```bash
python app.py
```

La aplicación estará disponible en:

```text
http://127.0.0.1:5000
```

También puedes acceder mediante:

```text
http://localhost:5000
```

---

## Usuario administrador por defecto

Si la base de datos se encuentra vacía, la aplicación crea automáticamente un usuario administrador.

```text
Usuario: admin
Contraseña: admin123
```

> **Importante:** cambia esta contraseña inmediatamente en un entorno de producción.

---

## Roles del sistema

El sistema utiliza autenticación basada en roles.

| Rol           | Funciones principales                             |
| ------------- | ------------------------------------------------- |
| Administrador | Gestión completa del sistema y usuarios           |
| Médico        | Consultas, diagnósticos, tratamientos y pacientes |
| Recepcionista | Gestión de pacientes y citas                      |
| Enfermería    | Gestión y seguimiento de hospitalizaciones        |

Los permisos pueden controlarse mediante los decoradores de autorización implementados en el proyecto.

---

## Estructura del proyecto

```text
HospitalArtoria/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── seed_db.py
├── decorators.py
│
├── database/
│   └── mongodb.py
│
├── models/
│   ├── paciente.py
│   ├── medico.py
│   ├── cita.py
│   ├── consulta.py
│   ├── diagnostico.py
│   ├── tratamiento.py
│   ├── hospitalizacion.py
│   └── pago.py
│
├── routes/
│   ├── auth.py
│   ├── pacientes.py
│   ├── medicos.py
│   ├── citas.py
│   ├── consultas.py
│   ├── diagnosticos.py
│   ├── tratamientos.py
│   ├── hospitalizaciones.py
│   ├── pagos.py
│   ├── reportes.py
│   └── machine_learning.py
│
├── services/
│   ├── analytics.py
│   ├── reports.py
│   └── data_service.py
│
├── ml/
│   ├── classification.py
│   ├── regression.py
│   ├── clustering.py
│   └── preprocessing.py
│
├── utils/
│   └── helpers.py
│
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
│
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── registro.html
    ├── pacientes.html
    ├── medicos.html
    ├── citas.html
    ├── consultas.html
    ├── diagnosticos.html
    ├── tratamientos.html
    ├── hospitalizaciones.html
    ├── reportes.html
    ├── machine_learning.html
    │
    └── admin/
        ├── dashboard.html
        └── usuarios.html
```

---

# Dashboard

El sistema cuenta con un dashboard diseñado para proporcionar una vista general del estado de la institución.

Entre los principales indicadores se encuentran:

* Total de pacientes.
* Total de médicos.
* Citas registradas.
* Consultas realizadas.
* Hospitalizaciones activas.
* Ingresos.
* Ocupación hospitalaria.
* Demanda por especialidad.
* Enfermedades más frecuentes.

Las gráficas son generadas mediante **Chart.js**.

---

# Machine Learning

El sistema incorpora un módulo de Machine Learning desarrollado con **Python, Pandas, NumPy y Scikit-learn**.

El objetivo es utilizar los datos hospitalarios para generar análisis predictivos que puedan apoyar la toma de decisiones.

## 1. Clasificación

### Predicción del riesgo de cancelación de citas

El modelo intenta determinar si una cita tiene una probabilidad alta o baja de ser cancelada.

Modelo utilizado:

```text
Random Forest Classifier
```

### Métricas

* Accuracy
* Precision
* Recall
* F1-Score
* Matriz de confusión

---

## 2. Regresión

La regresión permite realizar predicciones sobre variables numéricas.

### Predicción de demanda

El modelo puede utilizar información histórica para estimar la demanda futura de consultas.

### Predicción de costos

Permite estimar costos relacionados con la atención hospitalaria.

Modelo utilizado:

```text
Random Forest Regressor
```

### Métricas

* MAE
* MSE
* RMSE
* R²
* MAPE

---

## 3. Clustering

El clustering permite identificar grupos de pacientes con características similares.

Modelo utilizado:

```text
K-Means
```

Variables utilizadas inicialmente:

* Edad.
* Número de consultas.

Esto permite identificar diferentes perfiles de pacientes y facilitar el análisis de comportamiento.

---

## Flujo de Machine Learning

El procesamiento general de los modelos sigue el siguiente flujo:

```text
MongoDB Atlas
      │
      ▼
Extracción de datos
      │
      ▼
Pandas / NumPy
      │
      ▼
Preprocesamiento
      │
      ▼
Entrenamiento del modelo
      │
      ▼
Evaluación
      │
      ▼
Predicción
      │
      ▼
Visualización en Dashboard
```

Los datos se preprocesan antes de entrenar los modelos para evitar problemas relacionados con fechas, tipos de datos y objetos de MongoDB.

---

# Generación de informes

El sistema permite generar informes a partir de los datos almacenados en MongoDB.

## PDF

Los informes PDF se generan desde el navegador utilizando:

```text
html2pdf.js
```

Los informes pueden incluir:

* KPIs.
* Gráficas.
* Información de pacientes.
* Información de médicos.
* Estadísticas hospitalarias.
* Resultados del análisis.

El módulo de reportes puede ser accedido desde:

```text
/reportes
```

---

## ODF

El sistema también permite generar documentos en formato abierto mediante:

```text
odfpy
```

Los documentos `.odt` pueden incluir:

* KPIs.
* Estadísticas.
* Tablas.
* Información hospitalaria.

Los archivos son generados desde el servidor y enviados al navegador para su descarga.

---

# Seguridad

El proyecto implementa diferentes mecanismos de seguridad:

* Variables sensibles mediante `.env`.
* Autenticación de usuarios.
* Autorización mediante roles.
* Protección de rutas.
* Contraseñas almacenadas de forma segura.
* Separación de responsabilidades mediante módulos.
* `.env` excluido del repositorio mediante `.gitignore`.

### Importante

Nunca publiques información sensible como:

```text
MONGO_URI
GEMINI_API_KEY
SECRET_KEY
Contraseñas
Tokens
API Keys
```

El archivo `.env` debe permanecer fuera del repositorio.

---

# Despliegue en producción

## Render

Una opción recomendada para desplegar el sistema es **Render**.

### 1. Crear Procfile

Crea un archivo llamado:

```text
Procfile
```

Con el siguiente contenido:

```text
web: gunicorn app:app
```

### 2. Subir el proyecto a GitHub

```bash
git add .
git commit -m "Deploy HospitalArtoria"
git push origin main
```

### 3. Crear Web Service

En Render:

1. Crear un nuevo Web Service.
2. Conectar el repositorio de GitHub.
3. Seleccionar el repositorio del proyecto.
4. Configurar el entorno Python.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn app:app
```

### Variables de entorno

Agrega en Render las mismas variables configuradas en `.env`:

```text
MONGO_URI
DATABASE_NAME
SECRET_KEY
GEMINI_API_KEY
```

Después inicia el despliegue.

---

## Otras alternativas de despliegue

También es posible desplegar el proyecto utilizando:

* PythonAnywhere
* Koyeb
* Railway
* AWS
* Docker
* VPS

---

# Base de datos

El sistema utiliza **MongoDB Atlas** como base de datos principal.

La información se organiza mediante diferentes colecciones relacionadas con los módulos del sistema.

Entre las principales entidades se encuentran:

```text
usuarios
pacientes
medicos
citas
consultas
diagnosticos
tratamientos
hospitalizaciones
pagos
```

Se utilizan índices para optimizar las consultas más frecuentes y mejorar el rendimiento de la aplicación.

---

# Flujo general del sistema

```text
                    ┌─────────────────────┐
                    │       Usuario       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Autenticación     │
                    │      por roles      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Dashboard      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌────────────┐   ┌────────────┐
        │ Gestión   │    │ Analítica  │   │    ML      │
        │ hospital. │    │ Dashboard  │   │ Modelos    │
        └─────┬─────┘    └──────┬─────┘   └──────┬─────┘
              │                 │                │
              └─────────────────┼────────────────┘
                                ▼
                       ┌─────────────────┐
                       │   MongoDB Atlas │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Reportes     │
                       │    PDF / ODF    │
                       └─────────────────┘
```

---

# Comandos principales

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno en Windows

```powershell
venv\Scripts\activate
```

### Activar entorno en Linux/macOS

```bash
source venv/bin/activate
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Poblar la base de datos

```bash
python seed_db.py --clean
```

### Ejecutar la aplicación

```bash
python app.py
```

### Ejecutar en modo desarrollo

```bash
flask --app app run --debug
```

---

# Estado del proyecto

El proyecto está orientado a funcionar como una plataforma integral para la gestión y análisis de información hospitalaria.

Actualmente contempla:

* Gestión hospitalaria.
* Autenticación y autorización por roles.
* MongoDB Atlas.
* Dashboard analítico.
* Machine Learning.
* Predicciones.
* Clustering.
* Generación de informes.
* Exportación PDF.
* Exportación ODF.
* Generación de datos de prueba.
* Arquitectura modular mediante Flask.

---

# Mejoras futuras

Entre las posibles mejoras del proyecto se encuentran:

* Implementar un sistema avanzado de notificaciones.
* Integrar correo electrónico para recordatorios de citas.
* Implementar recuperación de contraseña.
* Mejorar el sistema de auditoría.
* Agregar historial médico completo.
* Incorporar modelos de Machine Learning adicionales.
* Implementar predicción de ocupación hospitalaria.
* Implementar predicción de costos hospitalarios.
* Mejorar la predicción de demanda.
* Agregar detección de anomalías.
* Incorporar modelos de Deep Learning.
* Implementar un sistema de recomendaciones.
* Agregar exportación a Excel.
* Incorporar generación automática de reportes.
* Mejorar el sistema de permisos.
* Implementar pruebas automatizadas.
* Implementar CI/CD.
* Containerizar la aplicación mediante Docker.

---

# Licencia

Este proyecto fue desarrollado con fines académicos y educativos.

La licencia y condiciones de distribución pueden definirse posteriormente de acuerdo con los objetivos del proyecto.

---

# Autor

**Uriel Valle Alejo**

Proyecto académico:

**Sistema Integral de Gestión Hospitalaria — HospitalArtoria**
