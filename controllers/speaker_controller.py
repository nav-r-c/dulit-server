from flask import request, jsonify
from models import Speaker
from bson.objectid import ObjectId

def create_speaker():
    data = request.json
    speaker = {
        "imageUrl" : data['imageUrl'],
        "name": data["name"],
        "bio": data["bio"],
        "programmes": data['programmes']
    }
    result = Speaker.create(speaker)
    return jsonify({"message": "Speaker created", "id": str(result.inserted_id)}), 201


def get_all_speakers():
    return jsonify(Speaker.get_all())


def get_speaker(speaker_id):
    speaker = Speaker.get_by_id(speaker_id)
    if not speaker:
        return jsonify({"error": "Speaker not found"}), 404
    return jsonify(speaker)


def update_speaker(speaker_id):
    data = request.json
    update_data = {key: data[key] for key in data if data[key] is not None}

    result = Speaker.update(speaker_id, update_data)

    if result.matched_count == 0:
        return jsonify({"error": "Speaker not found"}), 404

    return jsonify({"message": "Speaker updated"})


def delete_speaker(speaker_id):
    result = Speaker.delete(speaker_id)

    if result.deleted_count == 0:
        return jsonify({"error": "Speaker not found"}), 404

    return jsonify({"message": "Speaker deleted"})
