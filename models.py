from bson.objectid import ObjectId

def serialize_document(doc):
    """Convert MongoDB document to JSON serializable format."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

class Programme:
    collection = None  # Will be initialized in app.py

    @staticmethod
    def create(data):
        return Programme.collection.insert_one(data)

    @staticmethod
    def get_all():
        return [serialize_document(prog) for prog in Programme.collection.find()]

    @staticmethod
    def get_by_id(prog_id):
        return serialize_document(Programme.collection.find_one({"_id": ObjectId(prog_id)}))

    @staticmethod
    def update(prog_id, data):
        return Programme.collection.update_one({"_id": ObjectId(prog_id)}, {"$set": data})

    @staticmethod
    def delete(prog_id):
        return Programme.collection.delete_one({"_id": ObjectId(prog_id)})


class Speaker:
    collection = None  # Will be initialized in app.py

    @staticmethod
    def create(data):
        return Speaker.collection.insert_one(data)

    @staticmethod
    def get_all():
        return [serialize_document(spk) for spk in Speaker.collection.find()]

    @staticmethod
    def get_by_id(spk_id):
        return serialize_document(Speaker.collection.find_one({"_id": ObjectId(spk_id)}))

    @staticmethod
    def update(spk_id, data):
        return Speaker.collection.update_one({"_id": ObjectId(spk_id)}, {"$set": data})

    @staticmethod
    def delete(spk_id):
        return Speaker.collection.delete_one({"_id": ObjectId(spk_id)})
