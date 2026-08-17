from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.medicos import Medico
from decorators import login_required, role_required
from bson import ObjectId
from utils.helpers import convertir_objectid

medicos_bp = Blueprint('medicos', __name__)

@medicos_bp.route('/')
@login_required
@role_required('admin', 'recepcionista', 'medico')
def listar():
    return render_template('medicos.html')

@medicos_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'recepcionista', 'medico')
def api_listar():
    db = get_db()
    medicos = list(db.medicos.find())
    medicos = convertir_objectid(medicos)
    return jsonify(medicos)

@medicos_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'recepcionista')
def api_crear():
    data = request.json
    db = get_db()
    id = Medico.create(db, data)
    return jsonify({'_id': str(id)}), 201

@medicos_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'recepcionista')
def api_actualizar(id):
    data = request.json
    db = get_db()
    Medico.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@medicos_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar(id):
    db = get_db()
    Medico.delete(db, id)
    return jsonify({'message': 'eliminado'})