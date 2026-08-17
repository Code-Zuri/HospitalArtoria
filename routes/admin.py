from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.mongodb import get_db
from models.usuarios import Usuario
from decorators import login_required, role_required
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/usuarios')
@login_required
@role_required('admin')
def listar_usuarios():
    db = get_db()
    usuarios = Usuario.get_all(db)
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def crear_usuario():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        email = request.form.get('email')
        rol = request.form.get('rol')
        foto = request.files.get('foto_perfil')

        db = get_db()
        if Usuario.get_by_username(db, username):
            flash('El nombre de usuario ya existe', 'error')
            return render_template('admin/crear_usuario.html')

        foto_filename = None
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
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
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin.listar_usuarios'))
    return render_template('admin/crear_usuario.html')

@admin_bp.route('/usuarios/editar/<id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_usuario(id):
    db = get_db()
    usuario = Usuario.get_by_id(db, id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('admin.listar_usuarios'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellidos = request.form.get('apellidos')
        email = request.form.get('email')
        rol = request.form.get('rol')
        password = request.form.get('password')
        foto = request.files.get('foto_perfil')

        data = {
            'nombre': nombre,
            'apellidos': apellidos,
            'email': email,
            'rol': rol
        }
        if password:
            data['password'] = password

        # Manejar foto
        if foto and allowed_file(foto.filename):
            # Eliminar foto anterior si existe
            if usuario.get('foto_perfil'):
                old_path = os.path.join(UPLOAD_FOLDER, usuario['foto_perfil'])
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(foto.filename)
            import time
            name_parts = filename.rsplit('.', 1)
            new_filename = f"{usuario['username']}_{int(time.time())}.{name_parts[1]}"
            foto.save(os.path.join(UPLOAD_FOLDER, new_filename))
            data['foto_perfil'] = new_filename

        Usuario.update(db, id, data)
        flash('Usuario actualizado', 'success')
        return redirect(url_for('admin.listar_usuarios'))
    return render_template('admin/editar_usuario.html', usuario=usuario)

@admin_bp.route('/usuarios/eliminar/<id>', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_usuario(id):
    db = get_db()
    usuario = Usuario.get_by_id(db, id)
    if usuario:
        # Eliminar foto si existe
        if usuario.get('foto_perfil'):
            old_path = os.path.join(UPLOAD_FOLDER, usuario['foto_perfil'])
            if os.path.exists(old_path):
                os.remove(old_path)
        Usuario.delete(db, id)
        flash('Usuario eliminado', 'success')
    else:
        flash('Usuario no encontrado', 'error')
    return redirect(url_for('admin.listar_usuarios'))