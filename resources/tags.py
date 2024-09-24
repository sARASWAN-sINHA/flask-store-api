from json import dumps
from flask import Response
from flask_jwt_extended import jwt_required
from db import db
from models import Tags, Store, Items

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError


from schemas import TagSchema

tag_bp = Blueprint("tags", __name__, description="Operations on tags.")


@tag_bp.route("/store/<string:store_id>/tag")
class TagInStoreView(MethodView):

    @jwt_required()
    @tag_bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = Store.query.get_or_404(ident=store_id)
        return store.tags.all()

    @jwt_required()
    @tag_bp.response(201, TagSchema)
    @tag_bp.alt_response(
        500, description="When something goes wrong in the server side."
    )
    @tag_bp.arguments(TagSchema)
    def post(self, request_data, store_id):
        request_data["store_id"] = store_id
        try:
            new_tag = Tags(**request_data)
            db.session.add(new_tag)
            db.session.commit()
            return new_tag, 201
        except SQLAlchemyError as e:
            abort(
                500,
                f"Error occured while creating the new tag for this store. {str(e)}",
            )


@tag_bp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagToItem(MethodView):

    @jwt_required()
    @tag_bp.response(201, TagSchema)
    @tag_bp.alt_response(
        400,
        description="Returned when the store id of tag and the item to which the tag is assigned to do not match.",
        example={"detail": "Tag and the item must have same store."},
    )
    @tag_bp.alt_response(
        500,
        description="Returned when the tagging failed from server side.",
    )
    def post(self, item_id, tag_id):
        item = Items.query.get_or_404(item_id)
        tag = Tags.query.get_or_404(tag_id)

        if item.store.id == tag.store.id:
            try:
                item.tags.append(tag)

                db.session.add(item)
                db.session.commit()
            except SQLAlchemyError as e:
                abort(
                    500,
                    f"An error occured while linking this tag to the item.\n {str(e)}",
                )
            return tag
        abort(
            Response(dumps({"detail": "Tag and the item must have same store."}), 401)
        )

    @jwt_required()
    @tag_bp.response(
        202,
        TagSchema,
        description="Deletes a tag if no item is linked to it.",
    )
    @tag_bp.alt_response(
        404,
        description="Returned when either item or tag for the provided item_id or tag_id is not found.",
    )
    @tag_bp.alt_response(
        500,
        description="Returned when the un-linking failed from server side.",
    )
    def delete(self, item_id, tag_id):
        item = Items.query.get_or_404(item_id)
        tag = Tags.query.get_or_404(tag_id)

        try:
            item.tags.remove(tag)

            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                500,
                f"An error occured while un-linking this tag to the item. {str(e)}",
            )
        return tag


@tag_bp.route("/tag/<string:tag_id>")
class TagView(MethodView):

    @jwt_required()
    @tag_bp.response(200, TagSchema)
    @tag_bp.alt_response(404, description="Tag object for the given id not found.")
    def get(self, tag_id):
        tag = Tags.query.get_or_404(tag_id)
        return tag

    @jwt_required()
    @tag_bp.response(
        202,
        description="Deletes a tag if no item is linked to it.",
        example={"detail": "Tag deleted successfully."},
    )
    @tag_bp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case, tag is not deleted.",
    )
    @tag_bp.alt_response(404, description="Tag not found.")
    @tag_bp.alt_response(
        500,
        description="When some error occurrs while deleting the tag from server side.",
    )
    def delete(self, tag_id):
        tag = Tags.query.get_or_404(tag_id)

        if not tag.items:
            try:
                db.session.delete(tag)
                db.session.commit()
                return {"detail": "Tag deleted successfully."}
            except SQLAlchemyError:
                abort(500, "An error occurred while deleting the tag.")
        abort(400, "Could not delete tag since it was linked with one or more items.")
