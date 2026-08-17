from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    @staticmethod
    def create(db, data):
        # data: username, password, nombre, apellidos, email, rol, foto_perfil (opcional)
        data['password'] = generate_password_hash(data['password'])
        return db.usuarios.insert_one(data).inserted_id

    @staticmethod
    def get_by_username(db, username):
        return db.usuarios.find_one({'username': username})

    @staticmethod
    def get_by_id(db, id):
        return db.usuarios.find_one({'_id': ObjectId(id)})

    @staticmethod
    def check_password(usuario, password):
        return check_password_hash(usuario['password'], password)

    @staticmethod
    def update(db, id, data):
        if 'password' in data and data['password']:
            data['password'] = generate_password_hash(data['password'])
        else:
            data.pop('password', None)
        return db.usuarios.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.usuarios.delete_one({'_id': ObjectId(id)})

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.usuarios.find(filtro))