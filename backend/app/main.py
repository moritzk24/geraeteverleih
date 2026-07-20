from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ausleihen_router import router as ausleihen_router
from app.api.geraete_router import router as geraete_router
from app.api.import_router import router as import_router
from app.api.leihfristen_router import router as leihfristen_router
from app.api.reservierungen_router import router as reservierungen_router

app = FastAPI(title="Geräteverleih API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(import_router)
app.include_router(geraete_router)
app.include_router(ausleihen_router)
app.include_router(leihfristen_router)
app.include_router(reservierungen_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
