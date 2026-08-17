from bson import ObjectId

class Consulta:
    @staticmethod
    def create(db, data):
        return db.consultas.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.consultas.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.consultas.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.consultas.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.consultas.delete_one({'_id': ObjectId(id)})