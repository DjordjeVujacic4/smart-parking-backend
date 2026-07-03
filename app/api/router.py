from fastapi import APIRouter

from app.api import (
    auth,
    parking_locations,
    parking_sessions,
    reservations,
    users,
    vehicles,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(vehicles.router)
api_router.include_router(parking_locations.router)
api_router.include_router(reservations.router)
api_router.include_router(parking_sessions.router)
