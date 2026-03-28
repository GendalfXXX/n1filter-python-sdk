"""N1Filter AI Python SDK — client library for the N1Filter Generation API.

Quick start::

    from n1filter import N1FilterClient

    client = N1FilterClient("sk-your-api-key")
    balance = client.get_balance()
    print(f"Tokens: {balance.token_balance}")

For async usage::

    from n1filter import AsyncN1FilterClient

    async with AsyncN1FilterClient("sk-your-api-key") as client:
        order = await client.generate_image("photo.jpg", preset="undress")
        order = await client.wait_for_result(order.id)
"""

from n1filter._async_client import AsyncN1FilterClient
from n1filter._client import N1FilterClient
from n1filter._constants import SDK_VERSION as __version__
from n1filter._enums import ImagePreset, OrderStatus, VideoPreset
from n1filter._exceptions import (
    AuthenticationError,
    DownloadError,
    InsufficientBalanceError,
    N1FilterError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from n1filter._models import Balance, ImagePricing, Order, Preset, Prices, VideoPricing

__all__ = [
    # Clients
    "N1FilterClient",
    "AsyncN1FilterClient",
    # Models
    "Balance",
    "Order",
    "Prices",
    "Preset",
    "ImagePricing",
    "VideoPricing",
    # Enums
    "ImagePreset",
    "VideoPreset",
    "OrderStatus",
    # Exceptions
    "N1FilterError",
    "AuthenticationError",
    "InsufficientBalanceError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "DownloadError",
    # Meta
    "__version__",
]
