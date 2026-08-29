from .auth import router as auth_router
from .couple import router as couple_router
from .anniversary import router as anniversary_router
from .photo import router as photo_router
from .wish import router as wish_router
from .mood import router as mood_router
from .message import router as message_router
from .magazine import router as magazine_router
from .fund import router as fund_router
from .transaction import router as transaction_router
from .penalty import router as penalty_router
from .footprint import router as footprint_router
from .capsule import router as capsule_router
from .collection import router as collection_router
from .diary import router as diary_router

__all__ = [
    "auth_router", "couple_router",
    "anniversary_router", "photo_router", "wish_router",
    "mood_router", "message_router",
    "magazine_router",
    "fund_router", "transaction_router", "penalty_router",
    "footprint_router",
    "capsule_router",
    "collection_router",
    "diary_router",
]
