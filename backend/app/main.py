from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import predict, roadmap

app = FastAPI(title="HealthGuard AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tightened before real deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/predict", tags=["prediction"])
app.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
