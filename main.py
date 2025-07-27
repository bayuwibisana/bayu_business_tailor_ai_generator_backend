from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.batch import router as batch_router
from api.auth import router as auth_router
from api.campaigns import router as campaigns_router

app = FastAPI(title="Social Media Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(batch_router, prefix="/api", tags=["batch"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)