from fastapi import FastAPI

from routes.customer import router as customer_router

app = FastAPI(title="DRMS")

app.include_router(customer_router)


@app.get("/health")
def health():
    return {"status": "ok"}
