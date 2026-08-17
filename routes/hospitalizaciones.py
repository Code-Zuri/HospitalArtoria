from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.hospitalizaciones import Hospitalizacion
from decorators import login_required, role_required
from bson import ObjectId
from utils.helpers import convertir_objectid

hospitalizaciones_bp = Blueprint('hospitalizaciones', __name__)

@hospitalizaciones_bp.route('/')
@login_required
@role_required('admin', 'medico', 'enfermeria')
def listar():
    return render_template('hospitalizaciones.html')

@hospitalizaciones_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'medico', 'enfermeria')
def api_listar():
    db = get_db()
    hospitalizaciones = list(db.hospitalizaciones.find())
    hospitalizaciones = convertir_objectid(hospitalizaciones)
    return jsonify(hospitalizaciones)

@hospitalizaciones_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'medico')
def api_crear():
    data = request.json
    db = get_db()
    for campo in ['paciente_id', 'medico_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    id = Hospitalizacion.create(db, data)
    return jsonify({'_id': str(id)}), 201

@hospitalizaciones_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'medico', 'enfermeria')
def api_actualizar(id):
    data = request.json
    db = get_db()
    for campo in ['paciente_id', 'medico_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    Hospitalizacion.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@hospitalizaciones_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar(id):
    db = get_db()
    Hospitalizacion.delete(db, id)
    return jsonify({'message': 'eliminado'})