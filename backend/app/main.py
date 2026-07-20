from fastapi import FastAPI

from app.api.import_router import router as import_router

app = FastAPI(title="Geräteverleih API")
app.include_router(import_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
