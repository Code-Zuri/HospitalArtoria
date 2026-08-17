from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.pacientes import Paciente
from decorators import login_required, role_required
from bson import ObjectId
from utils.helpers import convertir_objectid

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/')
@login_required
@role_required('admin', 'recepcionista', 'medico')
def listar():
    return render_template('pacientes.html')

@pacientes_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'recepcionista', 'medico')
def api_listar():
    db = get_db()
    pacientes = list(db.pacientes.find())
    pacientes = convertir_objectid(pacientes)
    return jsonify(pacientes)

@pacientes_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'recepcionista')
def api_crear():
    data = request.json
    db = get_db()
    # Pacientes no tiene relaciones, solo el _id se genera automáticamente
    id = Paciente.create(db, data)
    return jsonify({'_id': str(id)}), 201

@pacientes_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'recepcionista', 'medico')
def api_actualizar(id):
    data = request.json
    db = get_db()
    Paciente.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@pacientes_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar(id):
    db = get_db()
    Paciente.delete(db, id)
    return jsonify({'message': 'eliminado'})