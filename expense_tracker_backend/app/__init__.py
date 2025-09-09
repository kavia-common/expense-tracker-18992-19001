from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .config import settings
from .utils import init_db
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.categories import blp as categories_blp
from .routes.expenses import blp as expenses_blp


app = Flask(__name__)
app.url_map.strict_slashes = False

# Load config and setup OpenAPI metadata
app.config["API_TITLE"] = settings.API_TITLE
app.config["API_VERSION"] = settings.API_VERSION
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = settings.OPENAPI_URL_PREFIX
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = settings.OPENAPI_SWAGGER_UI_URL

# CORS
cors_resources = {r"/*": {"origins": settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else "*"}}
CORS(app, resources=cors_resources)

# Initialize API and database
api = Api(app)
init_db()

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(categories_blp)
api.register_blueprint(expenses_blp)
