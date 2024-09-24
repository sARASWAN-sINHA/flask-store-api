from json import dumps
import os
from flask import Flask, Response
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from resources.items import items_bp as ItemBlueprint
from resources.store import store_bp as StoreBlueprint
from resources.tags import tag_bp as TagBlueprint
from resources.users import user_bp as UserBlueprint
from db import db


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)

    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "07105609e69f0a570ffe45ec8db66ef19beec327"
    app.config['JWT_HEADER_TYPE'] = 'JWT'
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_token):
        return (Response(dumps({"details": "Token expired."})), 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (Response(dumps({"details": "Invalid token."})), 401)

    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return (Response(dumps({"details": "No access token."})), 401)


    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
