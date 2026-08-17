from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.tratamientos import Tratamiento
from decorators import login_required, role_required
from bson import ObjectId
from utils.helpers import convertir_objectid

tratamientos_bp = Blueprint('tratamientos', __name__)

@tratamientos_bp.route('/')
@login_required
@role_required('admin', 'medico')
def listar():
    return render_template('tratamientos.html')

@tratamientos_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'medico')
def api_listar():
    db = get_db()
    tratamientos = list(db.tratamientos.find())
    tratamientos = convertir_objectid(tratamientos)
    return jsonify(tratamientos)

@tratamientos_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'medico')
def api_crear():
    data = request.json
    db = get_db()
    if 'consulta_id' in data and data['consulta_id']:
        data['consulta_id'] = ObjectId(data['consulta_id'])
    id = Tratamiento.create(db, data)
    return jsonify({'_id': str(id)}), 201

@tratamientos_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'medico')
def api_actualizar(id):
    data = request.json
    db = get_db()
    if 'consulta_id' in data and data['consulta_id']:
        data['consulta_id'] = ObjectId(data['consulta_id'])
    Tratamiento.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@tratamientos_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar(id):
    db = get_db()
    Tratamiento.delete(db, id)
    return jsonify({'message': 'eliminado'})