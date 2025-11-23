from fastapi import FastAPI
from app.database import engine, Base
from app.routes import brand_routes
from app.routes import user_routes
from app.models import brand as brand_model
from app.schemas import brand_schema
from fastapi.middleware.cors import CORSMiddleware

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Switch API", version="1.0.0")

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(brand_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Switch API!"}