from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.orm import Session

from ..schemas import (
    RegisterRequestSchema,
    LoginRequestSchema,
    AuthResponseSchema,
    UserSchema,
)
from ..models import User
from ..utils import create_access_token, SessionLocal

blp = Blueprint(
    "Auth",
    "auth",
    url_prefix="/api/auth",
    description="User authentication endpoints",
)


@blp.route("/register")
class Register(MethodView):
    @blp.arguments(RegisterRequestSchema, location="json")
    @blp.response(201, UserSchema, description="User registered")
    def post(self, payload):
        """Register a new user.
        ---
        summary: Register user
        description: Create a new user account with email and password.
        """
        email = payload["email"].lower().strip()
        password = payload["password"]
        name = payload.get("name")
        db: Session = SessionLocal()
        try:
            if db.query(User).filter(User.email == email).first():
                abort(409, message="Email already registered")
            user = User(email=email, name=name)
            user.set_password(password)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(LoginRequestSchema, location="json")
    @blp.response(200, AuthResponseSchema, description="JWT access token")
    def post(self, payload):
        """Login a user and return a JWT access token.
        ---
        summary: Login
        description: Validate credentials and return a signed JWT access token.
        """
        email = payload["email"].lower().strip()
        password = payload["password"]
        db: Session = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not user.check_password(password):
                abort(401, message="Invalid email or password")
            token = create_access_token(identity=user.email)
            return {"access_token": token}
        finally:
            db.close()
