from bson import ObjectId

class Pago:
    @staticmethod
    def create(db, data):
        return db.pagos.insert_one(data).inserted_id

    @staticmethod
    def get_all(db, filtro={}):
        return list(db.pagos.find(filtro))

    @staticmethod
    def get_by_id(db, id):
        return db.pagos.find_one({'_id': ObjectId(id)})

    @staticmethod
    def update(db, id, data):
        return db.pagos.update_one({'_id': ObjectId(id)}, {'$set': data})

    @staticmethod
    def delete(db, id):
        return db.pagos.delete_one({'_id': ObjectId(id)})