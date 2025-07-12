from aiogram import Router
from . import (
    registration,    
    profile,
    meet_command,
    meet_callbacks,
    info,
    common
)

def register_all(dp_router: Router):
    for module in (
        registration,
        profile,
        meet_command,
        meet_callbacks,
        info,
        common,
    ):
        dp_router.include_router(module.router)