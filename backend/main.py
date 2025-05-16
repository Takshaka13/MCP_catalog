from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.import_catalog import router as import_router

app = FastAPI(title="WB Analytics API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(import_router, prefix="/api", tags=["import"]) 