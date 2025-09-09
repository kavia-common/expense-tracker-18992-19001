from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint("Health", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    def get(self):
        """Health check endpoint.
        ---
        summary: Health check
        description: Returns a simple status message indicating the service is running.
        """
        return {"message": "Healthy"}
