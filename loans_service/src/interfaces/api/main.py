from fastapi import FastAPI
from .views import router


app = FastAPI(title="Loans Service", openapi_url="/openapi.json")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)