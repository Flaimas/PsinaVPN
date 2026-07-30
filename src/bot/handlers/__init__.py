from aiogram import Router

# from .errors import router as errors_router
from .payment import router as payment_router
from .start import router as start_router
from .sub_management import router as sub_managament_router
from .subscription import router as subscription_router

handlers_router = Router()
handlers_router.include_routers(
    # errors_router,
    start_router,
    subscription_router,
    payment_router,
    sub_managament_router,
)
