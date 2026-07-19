from .start import router as start_router
from .buy_menu import router as buy_menu_router
from aiogram import Router

handlers_router = Router()
handlers_router.include_routers(
    start_router,
    buy_menu_router,
)