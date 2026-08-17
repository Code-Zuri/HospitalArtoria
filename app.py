import os
from flask import Flask, render_template
from dotenv import load_dotenv
from database.mongodb import init_db
from models.usuarios import Usuario
from routes.auth import auth_bp
from routes.admin import admin_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key')

mongo = init_db(app)

# Registrar blueprints
from routes.pacientes import pacientes_bp
from routes.medicos import medicos_bp
from routes.citas import citas_bp
from routes.consultas import consultas_bp
from routes.diagnosticos import diagnosticos_bp
from routes.tratamientos import tratamientos_bp
from routes.hospitalizaciones import hospitalizaciones_bp
from routes.reportes import reportes_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(pacientes_bp, url_prefix='/pacientes')
app.register_blueprint(medicos_bp, url_prefix='/medicos')
app.register_blueprint(citas_bp, url_prefix='/citas')
app.register_blueprint(consultas_bp, url_prefix='/consultas')
app.register_blueprint(diagnosticos_bp, url_prefix='/diagnosticos')
app.register_blueprint(tratamientos_bp, url_prefix='/tratamientos')
app.register_blueprint(hospitalizaciones_bp, url_prefix='/hospitalizaciones')
app.register_blueprint(reportes_bp, url_prefix='/reportes')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/machine-learning')
def machine_learning():
    return render_template('machine_learning.html')

if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')

    with app.app_context():
        db = mongo
        # Crear usuario admin por defecto si no existe en la colección "usuarios"
        if db.usuarios.count_documents({}) == 0:
            admin_data = {
                'username': 'admin',
                'password': 'admin123',
                'nombre': 'Administrador',
                'apellidos': 'Sistema',
                'email': 'admin@hospital.artoria.com',
                'rol': 'admin',
                'foto_perfil': None
            }
            Usuario.create(db, admin_data)
            print("Usuario admin creado: admin / admin123")
        else:
            print("Ya existen usuarios en la colección 'usuarios'.")

    app.run(debug=True, host='0.0.0.0', port=5000)