from bson import ObjectId

class Paciente:
    @staticmethod
    def create(db, data):
        return db.pacientes.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.pacientes.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.pacientes.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.pacientes.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.pacientes.delete_one({'_id': ObjectId(id)})