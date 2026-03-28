"""Internal constants for the N1Filter SDK."""

SDK_VERSION: str = "0.1.0"
USER_AGENT: str = f"n1filter-python/{SDK_VERSION}"

DEFAULT_BASE_URL: str = "https://n1-filter.digital"
DEFAULT_TIMEOUT: float = 30.0
DOWNLOAD_TIMEOUT: float = 120.0
DEFAULT_POLL_INTERVAL: float = 2.0
DEFAULT_MAX_WAIT: float = 600.0

# API paths
PATH_BALANCE: str = "/api/v1/generation/balance"
PATH_PRICES: str = "/api/v1/generation/prices"
PATH_IMAGE: str = "/api/v1/generation/image"
PATH_VIDEO: str = "/api/v1/generation/video"
PATH_ORDERS: str = "/api/v1/generation/orders"
PATH_ORDER: str = "/api/v1/generation/orders/{order_id}"
PATH_DOWNLOAD: str = "/api/v1/generation/orders/{order_id}/download"
