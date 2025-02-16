from flask import Blueprint
from controllers.speaker_controller import (
    create_speaker, get_all_speakers, get_speaker, update_speaker, delete_speaker
)

speaker_bp = Blueprint("speaker_bp", __name__)

speaker_bp.route("/speakers", methods=["POST"])(create_speaker)
speaker_bp.route("/speakers", methods=["GET"])(get_all_speakers)
speaker_bp.route("/speakers/<speaker_id>", methods=["GET"])(get_speaker)
speaker_bp.route("/speakers/<speaker_id>", methods=["PUT"])(update_speaker)
speaker_bp.route("/speakers/<speaker_id>", methods=["DELETE"])(delete_speaker)
