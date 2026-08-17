from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.mongodb import get_db
from models.usuarios import Usuario
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

# Configuración de uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = Usuario.get_by_username(db, username)
        if user and Usuario.check_password(user, password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['rol'] = user.get('rol', 'usuario')
            session['foto_perfil'] = user.get('foto_perfil')
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        email = request.form.get('email')
        rol = request.form.get('rol', 'recepcionista')
        foto = request.files.get('foto_perfil')

        db = get_db()
        if Usuario.get_by_username(db, username):
            flash('El nombre de usuario ya existe', 'error')
            return render_template('registro.html')

        # Guardar foto si se subió
        foto_filename = None
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            # Renombrar para evitar colisiones: username + timestamp
            import time
            name_parts = filename.rsplit('.', 1)
            new_filename = f"{username}_{int(time.time())}.{name_parts[1]}"
            foto.save(os.path.join(UPLOAD_FOLDER, new_filename))
            foto_filename = new_filename

        data = {
            'username': username,
            'password': password,
            'nombre': nombre,
            'apellidos': apellidos,
            'email': email,
            'rol': rol,
            'foto_perfil': foto_filename
        }
        Usuario.create(db, data)
        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('auth.login'))
    return render_template('registro.html')