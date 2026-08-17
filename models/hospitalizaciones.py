from bson import ObjectId

class Hospitalizacion:
    @staticmethod
    def create(db, data):
        return db.hospitalizaciones.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.hospitalizaciones.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.hospitalizaciones.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.hospitalizaciones.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.hospitalizaciones.delete_one({'_id': ObjectId(id)})