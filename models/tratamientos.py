from bson import ObjectId

class Tratamiento:
    @staticmethod
    def create(db, data):
        return db.tratamientos.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.tratamientos.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.tratamientos.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.tratamientos.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.tratamientos.delete_one({'_id': ObjectId(id)})