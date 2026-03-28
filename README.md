# N1Filter AI Python SDK

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
Official Python client for the **N1Filter AI Generation API**. Generate AI images and videos with a simple, type-safe interface.

## Features

- **Sync & Async** — `N1FilterClient` for synchronous code, `AsyncN1FilterClient` for asyncio
- **Fully typed** — complete type annotations, `py.typed` marker (PEP 561)
- **Immutable models** — frozen dataclasses for all API responses
- **Flexible file input** — pass a file path (`str`), `Path` object, or raw `bytes`
- **Polling helper** — `wait_for_result()` polls until generation completes
- **Download helper** — save results to disk or get raw bytes
- **Smart errors** — specific exception types for every error scenario
- **Minimal deps** — only `httpx` as a runtime dependency

## Installation

```bash
pip install git+https://github.com/GendalfXXX/n1filter-python-sdk.git
```

## Quick Start

```python
from n1filter import N1FilterClient

client = N1FilterClient("sk-your-api-key", base_url="https://your-api.com")

# Check balance
balance = client.get_balance()
print(f"Tokens: {balance.token_balance}")

# View available presets and prices
prices = client.get_prices()
for preset in prices.image.presets:
    print(f"  {preset.id}: {preset.price} tokens")

# Generate an image
order = client.generate_image("photo.jpg", preset="undress")
print(f"Order #{order.id} — status: {order.status}")

# Wait for completion
order = client.wait_for_result(order.id)

if order.is_completed:
    # Download the result
    client.download(order.id, save_to="result.jpg")
    print("Saved to result.jpg")
elif order.is_failed:
    print(f"Generation failed: {order.error_msg}")

# Don't forget to close the client
client.close()
```

## Async Usage

```python
import asyncio
from n1filter import AsyncN1FilterClient

async def main():
    async with AsyncN1FilterClient("sk-your-api-key", base_url="https://your-api.com") as client:
        # Generate and wait in one call
        order = await client.generate_and_wait(
            "photo.jpg",
            preset="undress",
            type="image",
        )

        if order.is_completed:
            await client.download(order.id, save_to="result.jpg")

asyncio.run(main())
```

## File Input

All generation methods accept three types of image input:

```python
# 1. String path
order = client.generate_image("path/to/photo.jpg", preset="undress")

# 2. pathlib.Path
from pathlib import Path
order = client.generate_image(Path("photo.jpg"), preset="undress")

# 3. Raw bytes (e.g. from a web request or in-memory buffer)
image_bytes = open("photo.jpg", "rb").read()
order = client.generate_image(image_bytes, preset="undress")
```

Supported formats: **JPEG**, **PNG**, **WebP**. Maximum size: **5 MB**.

## Waiting for Results

Generation is asynchronous on the server. Use `wait_for_result()` to poll until the order reaches a terminal state:

```python
# Method 1: Generate, then wait separately
order = client.generate_image("photo.jpg", preset="undress")
order = client.wait_for_result(order.id, poll_interval=2.0, max_wait=600.0)

# Method 2: Generate and wait in one call
order = client.generate_and_wait("photo.jpg", preset="undress")
```

Parameters:
- `poll_interval` — seconds between status checks (default: `2.0`)
- `max_wait` — maximum wait time in seconds (default: `600.0` = 10 min)

## Downloading Results

```python
# Save to disk (creates parent directories automatically)
path = client.download(order.id, save_to="output/result.jpg")
print(f"Saved to {path}")

# Get raw bytes (for in-memory processing)
data = client.download_bytes(order.id)
```

Results are available for **24 hours** after completion.

## Error Handling

Every error type has its own exception class:

```python
from n1filter import (
    N1FilterClient,
    N1FilterError,
    AuthenticationError,
    InsufficientBalanceError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
)

client = N1FilterClient("sk-your-api-key", base_url="https://your-api.com")

try:
    order = client.generate_image("photo.jpg", preset="undress")
    order = client.wait_for_result(order.id)
except AuthenticationError:
    print("Invalid API key")
except InsufficientBalanceError:
    print("Not enough tokens — top up your balance")
except ValidationError as e:
    print(f"Bad request: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except TimeoutError as e:
    print(f"Order {e.order_id} timed out (last status: {e.last_status})")
except N1FilterError as e:
    print(f"API error: {e.message}")
```

| Exception | HTTP Status | When |
|---|---|---|
| `AuthenticationError` | 401, 403 | Invalid or missing API key |
| `InsufficientBalanceError` | 402 | Not enough tokens |
| `ValidationError` | 400, 422 | Bad parameters, file format, or size |
| `NotFoundError` | 404 | Order not found |
| `RateLimitError` | 429 | Too many requests |
| `ServerError` | 5xx | Server-side error |
| `TimeoutError` | — | Polling exceeded `max_wait` |
| `DownloadError` | — | Empty or failed download |

All exceptions inherit from `N1FilterError`.

## Available Presets

### Image Presets

| Preset | Enum |
|---|---|
| `undress` | `ImagePreset.UNDRESS` |
| `shibari_harness` | `ImagePreset.SHIBARI_HARNESS` |
| `bdsm_single` | `ImagePreset.BDSM_SINGLE` |
| `cowgirl` | `ImagePreset.COWGIRL` |
| `blowjob_pov` | `ImagePreset.BLOWJOB_POV` |
| `doggystyle_vaginal` | `ImagePreset.DOGGYSTYLE_VAGINAL` |

### Video Presets

| Preset | Enum |
|---|---|
| `undress` | `VideoPreset.UNDRESS` |
| `finger_masturbation` | `VideoPreset.FINGER_MASTURBATION` |
| `ahegao` | `VideoPreset.AHEGAO` |
| `blowjob` | `VideoPreset.BLOWJOB` |
| `blowjob_pov` | `VideoPreset.BLOWJOB_POV` |
| `doggystyle_vaginal` | `VideoPreset.DOGGYSTYLE_VAGINAL` |
| `missionary` | `VideoPreset.MISSIONARY` |
| `cowgirl` | `VideoPreset.COWGIRL` |
| `reverse_cowgirl` | `VideoPreset.REVERSE_COWGIRL` |
| `titjob` | `VideoPreset.TITJOB` |

Video duration: **4–8 seconds** (default: 4). Use the `seconds` parameter:

```python
order = client.generate_video("photo.jpg", preset="undress", seconds=6)
```

## API Reference

### `N1FilterClient` / `AsyncN1FilterClient`

```python
# Constructor
client = N1FilterClient(
    api_key: str,              # Your API key (sk-...)
    base_url: str = "...",     # API base URL
    timeout: float = 30.0,     # HTTP timeout (seconds)
)
```

#### Core Methods

| Method | Returns | Description |
|---|---|---|
| `get_balance()` | `Balance` | Current token balance |
| `get_prices()` | `Prices` | All presets with prices |
| `generate_image(image, preset)` | `Order` | Submit image generation |
| `generate_video(image, preset, *, seconds=4)` | `Order` | Submit video generation |
| `get_order(order_id)` | `Order` | Get order status |
| `list_orders(*, limit=50, offset=0)` | `list[Order]` | List user's orders |

#### Helper Methods

| Method | Returns | Description |
|---|---|---|
| `wait_for_result(order_id, *, poll_interval=2.0, max_wait=600.0)` | `Order` | Poll until terminal status |
| `download(order_id, save_to)` | `Path` | Save result to disk |
| `download_bytes(order_id)` | `bytes` | Get result as bytes |
| `generate_and_wait(image, preset, *, type="image", seconds=4, ...)` | `Order` | Generate + poll in one call |

#### Lifecycle

| Method | Description |
|---|---|
| `close()` | Close HTTP client and release connections |
| `with` / `async with` | Context manager for automatic cleanup |

### Models

```python
Balance.token_balance: int

Order.id: int
Order.user_id: int
Order.type: str                # "image" | "video"
Order.preset_id: str
Order.seconds: int | None      # video only
Order.status: str              # "pending" | "processing" | "completed" | "failed" | "canceled"
Order.tokens_spent: int
Order.tokens_refunded: bool
Order.result: str | None
Order.error_msg: str | None
Order.created_at: float        # unix timestamp
Order.completed_at: float | None
Order.is_terminal: bool        # property
Order.is_completed: bool       # property
Order.is_failed: bool          # property

Prices.image: ImagePricing
Prices.video: VideoPricing
ImagePricing.presets: tuple[Preset, ...]
VideoPricing.presets: tuple[Preset, ...]
VideoPricing.seconds_price: int
Preset.id: str
Preset.price: int
```

## Configuration

```python
# Custom base URL (self-hosted instance)
client = N1FilterClient("sk-...", base_url="https://my-instance.com")

# Custom timeout
client = N1FilterClient("sk-...", timeout=60.0)

# Custom polling parameters
order = client.wait_for_result(
    order_id,
    poll_interval=5.0,   # check every 5 seconds
    max_wait=1200.0,     # wait up to 20 minutes
)
```

## License

[MIT](LICENSE)
