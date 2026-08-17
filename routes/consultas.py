from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.consultas import Consulta
from decorators import login_required, role_required
from bson import ObjectId
from utils.helpers import convertir_objectid

consultas_bp = Blueprint('consultas', __name__)

@consultas_bp.route('/')
@login_required
@role_required('admin', 'medico', 'recepcionista')
def listar():
    return render_template('consultas.html')

@consultas_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'medico', 'recepcionista')
def api_listar():
    db = get_db()
    consultas = list(db.consultas.find())
    consultas = convertir_objectid(consultas)
    return jsonify(consultas)

@consultas_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'medico')
def api_crear():
    data = request.json
    db = get_db()
    # Convertir ids de string a ObjectId
    for campo in ['paciente_id', 'medico_id', 'cita_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    id = Consulta.create(db, data)
    return jsonify({'_id': str(id)}), 201

@consultas_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'medico')
def api_actualizar(id):
    data = request.json
    db = get_db()
    for campo in ['paciente_id', 'medico_id', 'cita_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    Consulta.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@consultas_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar(id):
    db = get_db()
    Consulta.delete(db, id)
    return jsonify({'message': 'eliminado'})