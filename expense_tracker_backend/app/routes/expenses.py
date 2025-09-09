from datetime import datetime

from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request, g
from sqlalchemy.orm import Session

from ..schemas import ExpenseCreateSchema, ExpenseUpdateSchema, ExpenseSchema, PaginationSchema
from ..utils import jwt_required, paginate, SessionLocal
from ..models import Expense, Category

blp = Blueprint(
    "Expenses",
    "expenses",
    url_prefix="/api/expenses",
    description="Expense CRUD endpoints",
)


@blp.route("")
class ExpenseList(MethodView):
    @jwt_required
    @blp.response(200, {
        "items": ExpenseSchema(many=True),
        "pagination": PaginationSchema
    })
    def get(self):
        """List expenses for current user with pagination and optional filters.
        ---
        summary: List expenses
        description: |
          Query params:
          - page (int, default 1)
          - page_size (int, max 100)
          - category_id (int)
          - date_from (ISO datetime)
          - date_to (ISO datetime)
        """
        page = int(request.args.get("page", "1"))
        page_size = int(request.args.get("page_size", "10"))
        category_id = request.args.get("category_id")
        date_from = request.args.get("date_from")
        date_to = request.args.get("date_to")

        db: Session = SessionLocal()
        try:
            q = db.query(Expense).filter(Expense.user_id == g.current_user.id).order_by(Expense.date.desc())
            if category_id:
                try:
                    cid = int(category_id)
                    q = q.filter(Expense.category_id == cid)
                except Exception:
                    abort(400, message="Invalid category_id")
            if date_from:
                try:
                    dt_from = datetime.fromisoformat(date_from)
                    q = q.filter(Expense.date >= dt_from)
                except Exception:
                    abort(400, message="Invalid date_from, expected ISO format")
            if date_to:
                try:
                    dt_to = datetime.fromisoformat(date_to)
                    q = q.filter(Expense.date <= dt_to)
                except Exception:
                    abort(400, message="Invalid date_to, expected ISO format")

            items, meta = paginate(q, page, page_size)
            return {"items": items, "pagination": meta}
        finally:
            db.close()

    @jwt_required
    @blp.arguments(ExpenseCreateSchema)
    @blp.response(201, ExpenseSchema)
    def post(self, payload):
        """Create an expense.
        ---
        summary: Create expense
        """
        db: Session = SessionLocal()
        try:
            category_id = payload.get("category_id")
            if category_id is not None:
                cat = (
                    db.query(Category)
                    .filter(Category.user_id == g.current_user.id, Category.id == category_id)
                    .first()
                )
                if not cat:
                    abort(400, message="Invalid category_id")

            exp = Expense(
                user_id=g.current_user.id,
                category_id=category_id,
                amount=payload["amount"],
                currency=payload.get("currency", "USD"),
                description=payload.get("description"),
                date=payload.get("date") or datetime.utcnow(),
            )
            db.add(exp)
            db.commit()
            db.refresh(exp)
            return exp
        finally:
            db.close()


@blp.route("/<int:expense_id>")
class ExpenseDetail(MethodView):
    @jwt_required
    @blp.response(200, ExpenseSchema)
    def get(self, expense_id: int):
        """Get an expense by ID.
        ---
        summary: Get expense
        """
        db: Session = SessionLocal()
        try:
            exp = (
                db.query(Expense)
                .filter(Expense.user_id == g.current_user.id, Expense.id == expense_id)
                .first()
            )
            if not exp:
                abort(404, message="Expense not found")
            return exp
        finally:
            db.close()

    @jwt_required
    @blp.arguments(ExpenseUpdateSchema)
    @blp.response(200, ExpenseSchema)
    def put(self, payload, expense_id: int):
        """Update an expense by ID.
        ---
        summary: Update expense
        """
        db: Session = SessionLocal()
        try:
            exp = (
                db.query(Expense)
                .filter(Expense.user_id == g.current_user.id, Expense.id == expense_id)
                .first()
            )
            if not exp:
                abort(404, message="Expense not found")

            if "category_id" in payload:
                cid = payload.get("category_id")
                if cid is not None:
                    cat = (
                        db.query(Category)
                        .filter(Category.user_id == g.current_user.id, Category.id == cid)
                        .first()
                    )
                    if not cat:
                        abort(400, message="Invalid category_id")
                exp.category_id = cid

            for key in ("amount", "currency", "description", "date"):
                if key in payload and payload[key] is not None:
                    setattr(exp, key, payload[key])

            db.commit()
            db.refresh(exp)
            return exp
        finally:
            db.close()

    @jwt_required
    @blp.response(204)
    def delete(self, expense_id: int):
        """Delete an expense by ID.
        ---
        summary: Delete expense
        """
        db: Session = SessionLocal()
        try:
            exp = (
                db.query(Expense)
                .filter(Expense.user_id == g.current_user.id, Expense.id == expense_id)
                .first()
            )
            if not exp:
                abort(404, message="Expense not found")
            db.delete(exp)
            db.commit()
            return ""
        finally:
            db.close()
