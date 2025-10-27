from fastapi import FastAPI
from app.database import engine, Base
from app.routes import brand_routes
from app.models import brand as brand_model
from app.schemas import brand_schema

app = FastAPI(title="Switch API", version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(brand_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Switch API!"}