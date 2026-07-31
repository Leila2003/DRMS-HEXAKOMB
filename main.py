from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.customer import router as customer_router
from utils.file_storage import UPLOAD_DIR

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="DRMS")

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.include_router(customer_router)


@app.get("/health")
def health():
    return {"status": "ok"}
