Sistema Integral de Gestión Hospitalaria
Sistema web para la administración, análisis y visualización de datos hospitalarios, con autenticación por roles y módulos de Machine Learning para la toma de decisiones.

📋 Descripción
Este sistema permite gestionar pacientes, médicos, citas, consultas, diagnósticos, tratamientos, hospitalizaciones y pagos. Incluye un dashboard interactivo con gráficas (Chart.js), un módulo de Machine Learning (clasificación, regresión y clustering) y la generación de informes en PDF y ODF. Está desarrollado con Flask, MongoDB Atlas y Python, y cuenta con un sistema de autenticación por roles (admin, médico, recepcionista, enfermería).

Características principales:

🔐 Autenticación con roles y gestión de usuarios.

🏥 CRUD completo para pacientes, médicos, citas, consultas, diagnósticos, tratamientos y hospitalizaciones.

📊 Dashboard con KPIs y gráficas interactivas (consultas por mes, demanda por especialidad, enfermedades frecuentes, ocupación, etc.).

🤖 Machine Learning: riesgo de cancelación de citas (clasificación), predicción de demanda y costos (regresión), clustering de pacientes.

📄 Generación de informes en PDF (desde el navegador con html2pdf.js) y en formato ODF (descarga desde el servidor).

🖼️ Subida de foto de perfil para usuarios del sistema.

🗄️ Base de datos MongoDB Atlas con índices optimizados.

🛠️ Tecnologías utilizadas
Tecnología	Versión	Propósito
Python	3.11+	Lenguaje de programación principal
Flask	2.3.3	Framework web para el backend
MongoDB Atlas	-	Base de datos NoSQL en la nube
PyMongo	4.6.1	Conector para MongoDB
Pandas	2.1.4	Manipulación y análisis de datos
NumPy	1.26.3	Operaciones numéricas
Scikit-learn	1.4.0	Machine Learning
Chart.js	3.9.1	Visualización de gráficas (CDN)
html2pdf.js	0.10.1	Generación de PDF desde el navegador
odfpy	1.4.1	Generación de informes ODF (opcional)
⚙️ Instalación y configuración
Requisitos previos
Python 3.11 o superior instalado.

Cuenta en MongoDB Atlas (o MongoDB local).

(Opcional) Clave de API de Gemini para el seeding con IA.

Pasos
Clonar el repositorio

bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
Crear y activar un entorno virtual

bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
Instalar dependencias

bash
pip install -r requirements.txt
Configurar variables de entorno

Crea un archivo .env en la raíz del proyecto con el siguiente contenido:

env
MONGO_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>.mongodb.net/
DATABASE_NAME=hospital_artoria
SECRET_KEY=tu_clave_secreta_aqui
GEMINI_API_KEY=tu_clave_de_gemini   # (opcional, solo para seeding)
MONGO_URI: Cadena de conexión a MongoDB Atlas (sin el nombre de la base de datos).

DATABASE_NAME: Nombre de la base de datos (ej. hospital_artoria).

SECRET_KEY: Clave secreta para las sesiones de Flask (puedes generarla con os.urandom(24).hex()).

GEMINI_API_KEY: Solo necesaria si deseas generar datos de prueba con Gemini (opcional).

Inicializar la base de datos (opcional)

Si quieres poblar la base de datos con datos de prueba, ejecuta:

bash
python seed_db.py --clean
Esto intentará generar datos con Gemini (si tienes la clave) o usará datos de respaldo generados aleatoriamente.

Ejecutar la aplicación

bash
python app.py
La aplicación estará disponible en http://127.0.0.1:5000.

👤 Usuario administrador por defecto
Si la base de datos está vacía, al ejecutar app.py se crea automáticamente un usuario administrador:

Usuario: admin

Contraseña: admin123

Cambia esta contraseña en producción.

📁 Estructura del proyecto
text
HospitalArtoria/
├── app.py                      # Punto de entrada
├── requirements.txt            # Dependencias
├── .env                        # Variables de entorno (no subir a git)
├── seed_db.py                  # Script para poblar la BD
├── decorators.py               # Decoradores de autenticación y roles
├── database/
│   └── mongodb.py              # Configuración de la conexión a MongoDB
├── models/                     # Modelos CRUD (pacientes, médicos, citas, etc.)
├── routes/                     # Rutas Flask (blueprints)
├── services/                   # Servicios de análisis y generación de datos
├── ml/                         # Módulo de Machine Learning
├── utils/                      # Utilidades (conversión de ObjectId, etc.)
├── static/                     # Archivos estáticos (CSS, JS, imágenes, uploads)
└── templates/                  # Plantillas HTML (Jinja2)
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
    └── admin/                  # Plantillas del panel de administración
🚀 Despliegue en producción
Render (recomendado)
Crea un archivo Procfile en la raíz con:

text
web: gunicorn app:app
Sube el proyecto a un repositorio de GitHub.

Ve a Render.com y crea un nuevo Web Service conectado a tu repositorio.

Configura el entorno:

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

Añade las mismas variables de entorno que en .env en el panel de Render.

Haz clic en Deploy. En minutos tu aplicación estará en línea en https://tu-servicio.onrender.com.

Nota: En el plan gratuito, la aplicación se "duerme" tras 15 minutos de inactividad; la primera visita puede tardar unos segundos en despertar.

Alternativas
PythonAnywhere: ideal para principiantes, con interfaz web clara.

Koyeb: similar a Render, con buen rendimiento.

Railway: fácil de usar, pero con un plan gratuito más limitado.

📊 Módulo de Machine Learning
El sistema incluye tres tipos de modelos:

Clasificación – Riesgo de cancelación de citas (Random Forest). Métricas: accuracy, precision, recall, F1-score, matriz de confusión.

Regresión – Predicción de demanda de consultas y costos de atención (Random Forest). Métricas: MAE, MSE, RMSE, R², MAPE.

Clustering – Agrupación de pacientes por edad y número de consultas (K-Means).

Los modelos se entrenan bajo demanda desde la interfaz /machine-learning. Los datos se preprocesan en Python (Pandas) para evitar problemas de conversión de fechas en MongoDB.

📄 Generación de informes
PDF: Se genera desde el navegador con html2pdf.js e incluye KPIs, 6 gráficas explicadas, tablas de pacientes (100) y médicos (50). Se activa desde el dashboard (/reportes).

ODF: Informe en formato abierto (.odt) que se descarga desde el servidor, con KPIs y tablas.