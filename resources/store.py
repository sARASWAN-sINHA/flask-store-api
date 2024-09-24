import uuid

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


from db import db
from models import Store
from schemas import StoreSchema


store_bp = Blueprint("store", __name__, description="Operations on store.")


@store_bp.route("/store")
class storeView(MethodView):

    @jwt_required()
    @store_bp.response(200, StoreSchema(many=True))
    def get(self):
        return Store.query.all()

    @jwt_required(fresh=True)
    @store_bp.arguments(schema=StoreSchema)
    @store_bp.response(200, StoreSchema)
    def post(self, request_data):
        store = Store(**request_data)
        try:
            db.session.add(store)
            db.session.commit()
            return store
        except IntegrityError as e:
            abort(400, e)


@store_bp.route("/store/<string:id>")
class storeDetailView(MethodView):

    @jwt_required()
    @store_bp.response(200, StoreSchema)
    def get(self, id):
        store = Store.query.get_or_404(id)
        return store

    @jwt_required(fresh=True)
    def delete(self, id):
        store = Store.query.get_or_404(id)
        db.session.delete(store)
        db.session.commit()
        return {"detail": "Item deleted sucessfully."}, 200
