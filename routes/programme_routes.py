from flask import Blueprint
from controllers.programme_controller import (
    create_programme, get_all_programmes, get_programme, update_programme, delete_programme
)

programme_bp = Blueprint("programme_bp", __name__)

programme_bp.route("/programmes", methods=["POST"])(create_programme)
programme_bp.route("/programmes", methods=["GET"])(get_all_programmes)
programme_bp.route("/programmes/<programme_id>", methods=["GET"])(get_programme)
programme_bp.route("/programmes/<programme_id>", methods=["PUT"])(update_programme)
programme_bp.route("/programmes/<programme_id>", methods=["DELETE"])(delete_programme)
