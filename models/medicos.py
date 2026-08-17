from bson import ObjectId

class Medico:
    @staticmethod
    def create(db, data):
        return db.medicos.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.medicos.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.medicos.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.medicos.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.medicos.delete_one({'_id': ObjectId(id)})