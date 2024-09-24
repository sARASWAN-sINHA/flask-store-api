from json import dumps
from flask import Response
from flask_smorest import abort, Blueprint
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
)

from models import Users
from db import db
from schemas import UserSchema

user_bp = Blueprint("Users", __name__, description="Operations on users.")


@user_bp.route("/users")
class UserView(MethodView):

    @user_bp.arguments(UserSchema)
    @user_bp.response(
        201,
        description="Returned when new user is created and it's details are saved in the database.",
        example={"details": "Error while saving the user form the server side"},
    )
    @user_bp.response(
        409,
        description="Returned when username for new user already exists.",
        example={"details": "Username already exists."},
    )
    @user_bp.alt_response(
        500,
        description="Returned when there is a server side issue while saving the details of the new user in the database.",
        example={"details": "Error while saving the user form the server side"},
    )
    def post(self, request_data):
        password = request_data.get("password")
        hashed_password = pbkdf2_sha256.hash(password)
        request_data["password"] = hashed_password
        try:
            user = Users(**request_data)
            db.session.add(user)
            db.session.commit()
            return {"details": "User created successfully."}, 201
        except IntegrityError:
            abort(Response(dumps({"details": "Username already exists."}), 409))
        except SQLAlchemyError:
            abort(
                Response(
                    dumps(
                        {"details": "Error while saving the user form the server side"}
                    ),
                    500,
                )
            )


@user_bp.route("/users/<int:user_id>")
class UserDetailsView(MethodView):

    @user_bp.response(200, UserSchema)
    @user_bp.alt_response(
        404,
        description="Returned when user_id is invalid, or user for the given user_id is not found.",
    )
    def get(self, user_id):
        user = Users.query.get_or_404(user_id)
        return user

    @user_bp.response(
        202,
        description="Returned when user is deleted from the database.",
        example={"details": "User deleted successfully."},
    )
    @user_bp.alt_response(
        404,
        description="Returned when user_id is invalid, or user for the givenuser_id is not found.",
    )
    @user_bp.alt_response(
        500,
        description="Returned when there is a server side issue while deleting the details of the new user in the database.",
        example={"details": "Error while deleting the user form the server side"},
    )
    def delete(self, user_id):
        user = Users.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            return {"details": "User deleted successfully."}, 202
        except SQLAlchemyError:
            abort(
                Response(
                    dumps(
                        {
                            "details": "Error while deleting the user form the server side"
                        }
                    ),
                    500,
                )
            )


@user_bp.route("/login")
class UserLoginView(MethodView):

    @user_bp.arguments(UserSchema)
    @user_bp.response(
        201,
        description="Returned when user details(username and password) are validated correctly and generates an access token.",
        example={"access": "JWT_TOKEN"},
    )
    @user_bp.response(
        401,
        description="Returned when user details(username and password) do not match any user.",
        example={"details": "Invalid credentials"},
    )
    def post(self, request_data):
        user = Users.query.filter(
            Users.username == request_data.get("username")
        ).first()
        if user and pbkdf2_sha256.verify(request_data.get("password"), user.password):
            access_token, refresh_token = create_access_token(
                identity=user.id, fresh=True
            ), create_refresh_token(identity=user.id)
            return {"access": access_token, "refresh": refresh_token}, 201
        abort(Response(dumps({"details": "Invalid credentials"}), 401))


@user_bp.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt().get("sub")
        access_token = create_access_token(identity=user_id, fresh=False)
        return {"access": access_token}, 201
