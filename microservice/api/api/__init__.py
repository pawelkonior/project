from api.widgets import router as widget_router
from api.users import router as user_router
from api.auth import router as auth_router
from api.metrics import router as metrics_router

routers = [
    widget_router,
    user_router,
    auth_router,
    metrics_router,
]
