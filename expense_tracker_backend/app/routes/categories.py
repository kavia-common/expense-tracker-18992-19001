from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import g
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..schemas import CategoryCreateSchema, CategoryUpdateSchema, CategorySchema
from ..utils import jwt_required, SessionLocal
from ..models import Category

blp = Blueprint(
    "Categories",
    "categories",
    url_prefix="/api/categories",
    description="Expense category management",
)


@blp.route("")
class CategoryList(MethodView):
    @jwt_required
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        """List categories for the current user.
        ---
        summary: List categories
        """
        db: Session = SessionLocal()
        try:
            q = db.query(Category).filter(Category.user_id == g.current_user.id).order_by(Category.name.asc())
            categories = q.all()
            return categories
        finally:
            db.close()

    @jwt_required
    @blp.arguments(CategoryCreateSchema)
    @blp.response(201, CategorySchema)
    def post(self, payload):
        """Create a new category for the user.
        ---
        summary: Create category
        """
        db: Session = SessionLocal()
        try:
            cat = Category(
                name=payload["name"].strip(),
                color=payload.get("color"),
                user_id=g.current_user.id,
            )
            db.add(cat)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                abort(409, message="Category with this name already exists")
            db.refresh(cat)
            return cat
        finally:
            db.close()


@blp.route("/<int:category_id>")
class CategoryDetail(MethodView):
    @jwt_required
    @blp.response(200, CategorySchema)
    def get(self, category_id: int):
        """Get a category by ID.
        ---
        summary: Get category
        """
        db: Session = SessionLocal()
        try:
            cat = (
                db.query(Category)
                .filter(Category.user_id == g.current_user.id, Category.id == category_id)
                .first()
            )
            if not cat:
                abort(404, message="Category not found")
            return cat
        finally:
            db.close()

    @jwt_required
    @blp.arguments(CategoryUpdateSchema)
    @blp.response(200, CategorySchema)
    def put(self, payload, category_id: int):
        """Update a category by ID.
        ---
        summary: Update category
        """
        db: Session = SessionLocal()
        try:
            cat = (
                db.query(Category)
                .filter(Category.user_id == g.current_user.id, Category.id == category_id)
                .first()
            )
            if not cat:
                abort(404, message="Category not found")
            if "name" in payload and payload["name"] is not None:
                cat.name = payload["name"].strip()
            if "color" in payload:
                cat.color = payload["color"]
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                abort(409, message="Category with this name already exists")
            db.refresh(cat)
            return cat
        finally:
            db.close()

    @jwt_required
    @blp.response(204)
    def delete(self, category_id: int):
        """Delete a category by ID.
        ---
        summary: Delete category
        """
        db: Session = SessionLocal()
        try:
            cat = (
                db.query(Category)
                .filter(Category.user_id == g.current_user.id, Category.id == category_id)
                .first()
            )
            if not cat:
                abort(404, message="Category not found")
            db.delete(cat)
            db.commit()
            return ""
        finally:
            db.close()
