from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.citas import Cita
from decorators import login_required, role_required
from bson import ObjectId
from utils.helpers import convertir_objectid

citas_bp = Blueprint('citas', __name__)

@citas_bp.route('/')
@login_required
@role_required('admin', 'recepcionista', 'medico', 'enfermeria')
def listar():
    return render_template('citas.html')

@citas_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'recepcionista', 'medico', 'enfermeria')
def api_listar():
    db = get_db()
    citas = list(db.citas.find())
    citas = convertir_objectid(citas)
    return jsonify(citas)

@citas_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'recepcionista', 'medico')
def api_crear():
    data = request.json
    db = get_db()
    for campo in ['paciente_id', 'medico_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    id = Cita.create(db, data)
    return jsonify({'_id': str(id)}), 201

@citas_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'recepcionista', 'medico')
def api_actualizar(id):
    data = request.json
    db = get_db()
    for campo in ['paciente_id', 'medico_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    Cita.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@citas_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin', 'recepcionista')
def api_eliminar(id):
    db = get_db()
    Cita.delete(db, id)
    return jsonify({'message': 'eliminado'})