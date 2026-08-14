from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import service.auth as auth_service
from database.database import SessionLocal
from routes.analytics import router as analytics_router
from routes.auth import router as auth_router
from routes.booking import router as booking_router
from routes.category import router as category_router
from routes.customer import router as customer_router
from routes.notification import router as notification_router
from utils.file_storage import UPLOAD_DIR

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Swagger groups endpoints by role rather than by resource. openapi_tags
# pins the section order (Auth, then Admin, then Staff) regardless of route
# registration order, and gives each section a one-line description.
app = FastAPI(
    title="DRMS",
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Login and session identity, shared by both roles.",
        },
        {
            "name": "Admin",
            "description": "Everything the admin can do: staff account management, "
            "analytics, plus every Staff-permitted endpoint below.",
        },
        {
            "name": "Staff",
            "description": "Everything a staff member can do: bookings, customers, "
            "categories, and notifications.",
        },
    ],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(category_router)
app.include_router(booking_router)
app.include_router(notification_router)
app.include_router(analytics_router)


@app.on_event("startup")
def seed_default_admin():
    db = SessionLocal()
    try:
        auth_service.seed_default_admin(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
