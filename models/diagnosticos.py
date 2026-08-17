from bson import ObjectId

class Diagnostico:
    @staticmethod
    def create(db, data):
        return db.diagnosticos.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.diagnosticos.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.diagnosticos.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.diagnosticos.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.diagnosticos.delete_one({'_id': ObjectId(id)})