from aiogram import Router
from . import (
    registration,    
    profile,
    meet_command,
    meet_callbacks,
    info,
    office,
    common
)

def register_all(dp_router: Router):
    for module in (
        registration,
        profile,
        meet_command,
        meet_callbacks,
        info,
        office,
        common,
    ):
        dp_router.include_router(module.router)