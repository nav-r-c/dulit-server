from flask import request, jsonify
from models import Programme
from bson.objectid import ObjectId

def create_programme():
    data = request.json
    programme = {
        "name": data["name"],
        "description": data["description"],
        "day_number": data["day_number"],
        "date": data["date"],
        "start_datetime": data["start_datetime"],
        "end_datetime": data["end_datetime"],
        "venue": data["venue"]
    }
    result = Programme.create(programme)
    return jsonify({"message": "Programme created", "id": str(result.inserted_id)}), 201


def get_all_programmes():
    return jsonify(Programme.get_all())


def get_programme(programme_id):
    programme = Programme.get_by_id(programme_id)
    if not programme:
        return jsonify({"error": "Programme not found"}), 404
    return jsonify(programme)


def update_programme(programme_id):
    data = request.json
    update_data = {key: data[key] for key in data if data[key] is not None}
    result = Programme.update(programme_id, update_data)

    if result.matched_count == 0:
        return jsonify({"error": "Programme not found"}), 404

    return jsonify({"message": "Programme updated"})


def delete_programme(programme_id):
    result = Programme.delete(programme_id)

    if result.deleted_count == 0:
        return jsonify({"error": "Programme not found"}), 404

    return jsonify({"message": "Programme deleted"})
