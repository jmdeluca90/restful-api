from fastapi import FastAPI
from app.routers import auth, users, oauth
from app.database import engine, Base

# Create tables (in production, use Alembic for migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advanced FastAPI Example", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(oauth.router)