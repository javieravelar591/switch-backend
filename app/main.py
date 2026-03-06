from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.database import engine, Base
from app.routes import brand_routes
from app.routes import user_routes
from app.models import brand as brand_model          # noqa: must import before brand_article
from app.models import brand_article                 # noqa: registers BrandArticle with Base
from app.schemas import brand_schema
from fastapi.middleware.cors import CORSMiddleware

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Switch API", version="1.0.0", redirect_slashes=False)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

import os
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

Base.metadata.create_all(bind=engine)

app.include_router(brand_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Switch API!"}