from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import Bookmark, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/bookmarks")

@bookmarks.post("/")
@jwt_required()
def create_bookmark():
    user_id = get_jwt_identity()
    data = request.get_json()

    bookmark = Bookmark(**data)
    bookmark.user_id = user_id
    db.session.add(bookmark)
    db.session.commit()
    return jsonify(bookmark.to_dict()),HTTP_200_OK

@bookmarks.get("/")
@jwt_required()
def get_all():
    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Bookmark.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)

    # Convert each bookmark object to dict
    user_bookmarks = [bookmark.to_dict() for bookmark in pagination .items]

    meta={
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "has_prev_page": pagination.has_prev,
        "has_next_page": pagination.has_next,
        "prev_page": pagination.prev_num,
        "next_page": pagination.next_num,
    }

    return jsonify({"meta": meta, "data": user_bookmarks}), HTTP_200_OK

@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    bookmark = Bookmark.query.filter_by(id=id).first()

    if not bookmark:
        return jsonify({"msg": "Bookmark not found"}), HTTP_404_NOT_FOUND

    return jsonify(bookmark.to_dict()), HTTP_200_OK

@bookmarks.put("/<int:id>")
@jwt_required()
def update_bookmark(id):

    bookmark = Bookmark.query.filter_by(id=id).first()
    if not bookmark:
        return jsonify({"msg": "Bookmark not found"}), HTTP_404_NOT_FOUND

    data = request.get_json()

    bookmark.update(**data)
    db.session.commit()

    return jsonify(bookmark.to_dict()), HTTP_200_OK

@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    bookmark = Bookmark.query.filter_by(id=id).first()

    if not bookmark:
        return jsonify({"msg": "Bookmark not found"}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({"msg": "Bookmark deleted"}), HTTP_200_OK
