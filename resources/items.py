from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

from db import db
from schemas import ItemSchema, ItemUpdateSchema
from models import Items, Store

items_bp = Blueprint("items", __name__, description="Operations on Items.")


@items_bp.route("/item")
class ItemsView(MethodView):

    @jwt_required()
    @items_bp.response(200, ItemSchema(many=True))
    def get(self):
        return Items.query.all()

    @jwt_required()
    @items_bp.arguments(ItemSchema)
    @items_bp.response(200, ItemSchema)
    def post(self, request_data):
        item = Items(**request_data)
        try:
            db.session.add(item)
            db.session.commit()
            return {"detail": "Item created sucessfully."}, 200
        except SQLAlchemyError:
            abort(500, "An error occured while adding item to database.")


@items_bp.route("/item/<string:id>")
class ItemsDetailView(MethodView):

    @jwt_required()
    @items_bp.response(200, ItemSchema)
    def get(self, id):
        item = Items.query.get_or_404(id)
        return item

    def delete(sel, id):
        item = Items.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()

        return {"detail": "Item deleted sucessfully."}, 200

    @jwt_required()
    @items_bp.arguments(ItemUpdateSchema)
    @items_bp.response(200, ItemSchema)
    def put(self, request_data, id):
        item = Items.query.get_or_404(id)

        item.name = request_data.get("name", item.name)
        item.price = request_data.get("price", item.price)

        db.session.add(item)
        db.session.commit()

        return {"detail": "Item updated sucessfully."}, 200
