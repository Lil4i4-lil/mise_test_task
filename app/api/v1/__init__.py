from fastapi import APIRouter

from app.api.v1.booking import router as booking_router


router = APIRouter()

router.include_router(booking_router)
