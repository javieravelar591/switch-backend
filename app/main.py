from fastapi import FastAPI
from app.database import engine, Base
from app.routes import brand_routes
from app.models import brand as brand_model
from app.schemas import brand_schema
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Switch API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # your frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(brand_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Switch API!"}