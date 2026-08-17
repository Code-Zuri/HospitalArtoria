from flask import Blueprint, request, jsonify, render_template
from database.mongodb import get_db
from models.diagnosticos import Diagnostico
from decorators import login_required, role_required
from bson import ObjectId

diagnosticos_bp = Blueprint('diagnosticos', __name__)

# Helper para convertir ObjectId a string en listas
def convertir_objectid(documento):
    if isinstance(documento, list):
        return [convertir_objectid(d) for d in documento]
    if isinstance(documento, dict):
        for clave, valor in documento.items():
            if isinstance(valor, ObjectId):
                documento[clave] = str(valor)
            elif isinstance(valor, (list, dict)):
                documento[clave] = convertir_objectid(valor)
    return documento

@diagnosticos_bp.route('/')
@login_required
@role_required('admin', 'medico')
def listar():
    return render_template('diagnosticos.html')

@diagnosticos_bp.route('/api', methods=['GET'])
@login_required
@role_required('admin', 'medico')
def api_listar():
    db = get_db()
    diagnosticos = list(db.diagnosticos.find())
    # Convertir ObjectId a string
    diagnosticos = convertir_objectid(diagnosticos)
    return jsonify(diagnosticos)

@diagnosticos_bp.route('/api', methods=['POST'])
@login_required
@role_required('admin', 'medico')
def api_crear():
    data = request.json
    db = get_db()
    # Convertir ids de string a ObjectId si vienen en la petición
    if 'paciente_id' in data and data['paciente_id']:
        data['paciente_id'] = ObjectId(data['paciente_id'])
    if 'medico_id' in data and data['medico_id']:
        data['medico_id'] = ObjectId(data['medico_id'])
    if 'consulta_id' in data and data['consulta_id']:
        data['consulta_id'] = ObjectId(data['consulta_id'])
    id = Diagnostico.create(db, data)
    return jsonify({'_id': str(id)}), 201

@diagnosticos_bp.route('/api/<id>', methods=['PUT'])
@login_required
@role_required('admin', 'medico')
def api_actualizar(id):
    data = request.json
    db = get_db()
    # Convertir ids a ObjectId
    for campo in ['paciente_id', 'medico_id', 'consulta_id']:
        if campo in data and data[campo]:
            data[campo] = ObjectId(data[campo])
    Diagnostico.update(db, id, data)
    return jsonify({'message': 'actualizado'})

@diagnosticos_bp.route('/api/<id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_eliminar(id):
    db = get_db()
    Diagnostico.delete(db, id)
    return jsonify({'message': 'eliminado'})