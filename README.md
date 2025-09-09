# expense-tracker-18992-19001

Backend (Flask) - Expense Tracker

- Location: expense_tracker_backend/
- API Docs: served at /docs (OpenAPI 3 via flask-smorest)

Setup

1) Create and populate .env
   cp expense_tracker_backend/.env.example expense_tracker_backend/.env
   # Edit DB_URL and JWT_SECRET_KEY

2) Install dependencies
   pip install -r expense_tracker_backend/requirements.txt

3) Run the server
   cd expense_tracker_backend
   python run.py

Environment variables

- DB_URL: SQLAlchemy database URL (e.g., postgresql+psycopg2://user:pass@host:5432/dbname)
- JWT_SECRET_KEY: Secret key for signing JWT tokens
- JWT_ACCESS_TOKEN_EXPIRES_MIN: Access token expiry in minutes (default 60)
- CORS_ORIGINS: Comma-separated origins or * (default *)
- API_TITLE, API_VERSION, OPENAPI_URL_PREFIX, OPENAPI_SWAGGER_UI_URL: Optional customization

Main endpoints

- Health: GET /
- Auth:
  - POST /api/auth/register
  - POST /api/auth/login
- Categories:
  - GET /api/categories
  - POST /api/categories
  - GET /api/categories/{id}
  - PUT /api/categories/{id}
  - DELETE /api/categories/{id}
- Expenses:
  - GET /api/expenses?page=1&page_size=10&category_id=&date_from=&date_to=
  - POST /api/expenses
  - GET /api/expenses/{id}
  - PUT /api/expenses/{id}
  - DELETE /api/expenses/{id}