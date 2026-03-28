"""Immutable dataclass models for N1Filter API responses.

All models are frozen (immutable) and use ``__slots__`` for memory efficiency.
Each model provides a :meth:`from_dict` class method for constructing instances
from raw JSON dictionaries returned by the API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ── Pricing ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Preset:
    """A single generation preset with its token cost.

    Attributes:
        id: Preset identifier (e.g. ``"undress"``, ``"cowgirl"``).
        price: Cost in tokens for one generation with this preset.
    """

    id: str
    price: int

    @classmethod
    def from_dict(cls, data: dict) -> Preset:
        return cls(id=data["id"], price=data["price"])


@dataclass(frozen=True, slots=True)
class ImagePricing:
    """Pricing information for image generation.

    Attributes:
        presets: Available image presets and their prices.
    """

    presets: tuple[Preset, ...]

    @classmethod
    def from_dict(cls, data: dict) -> ImagePricing:
        return cls(presets=tuple(Preset.from_dict(p) for p in data["presets"]))


@dataclass(frozen=True, slots=True)
class VideoPricing:
    """Pricing information for video generation.

    Attributes:
        presets: Available video presets and their prices.
        seconds_price: Additional cost per second of video duration.
    """

    presets: tuple[Preset, ...]
    seconds_price: int

    @classmethod
    def from_dict(cls, data: dict) -> VideoPricing:
        return cls(
            presets=tuple(Preset.from_dict(p) for p in data["presets"]),
            seconds_price=data["seconds_price"],
        )


@dataclass(frozen=True, slots=True)
class Prices:
    """Complete pricing structure for all generation types.

    Attributes:
        image: Image generation pricing.
        video: Video generation pricing.
    """

    image: ImagePricing
    video: VideoPricing

    @classmethod
    def from_dict(cls, data: dict) -> Prices:
        gen = data["generation"]
        return cls(
            image=ImagePricing.from_dict(gen["image"]),
            video=VideoPricing.from_dict(gen["video"]),
        )


# ── Balance ──────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Balance:
    """User's current token balance.

    Attributes:
        token_balance: Number of tokens available for generation.
    """

    token_balance: int

    @classmethod
    def from_dict(cls, data: dict) -> Balance:
        return cls(token_balance=data["token_balance"])


# ── Order ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Order:
    """A generation order with its current status and metadata.

    Attributes:
        id: Unique order identifier.
        user_id: ID of the user who created the order.
        type: Generation type — ``"image"`` or ``"video"``.
        preset_id: Preset used for this generation.
        seconds: Video duration in seconds (``None`` for images).
        status: Current order status. One of: ``"pending"``,
            ``"processing"``, ``"completed"``, ``"failed"``, ``"canceled"``.
        tokens_spent: Number of tokens charged for this order.
        tokens_refunded: Whether tokens were refunded (on failure/cancellation).
        result: Result filename on the server (``None`` if not yet completed).
        error_msg: Error description (``None`` if no error occurred).
        created_at: Unix timestamp of order creation.
        completed_at: Unix timestamp of completion (``None`` if not yet completed).
    """

    id: int
    user_id: int
    type: str
    preset_id: str
    seconds: Optional[int]
    status: str
    tokens_spent: int
    tokens_refunded: bool
    result: Optional[str]
    error_msg: Optional[str]
    created_at: float
    completed_at: Optional[float]

    @classmethod
    def from_dict(cls, data: dict) -> Order:
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            type=data["type"],
            preset_id=data["preset_id"],
            seconds=data.get("seconds"),
            status=data["status"],
            tokens_spent=data["tokens_spent"],
            tokens_refunded=data["tokens_refunded"],
            result=data.get("result"),
            error_msg=data.get("error_msg"),
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
        )

    @property
    def is_terminal(self) -> bool:
        """``True`` if the order has reached a final state.

        Terminal statuses: ``completed``, ``failed``, ``canceled``.
        """
        return self.status in ("completed", "failed", "canceled")

    @property
    def is_completed(self) -> bool:
        """``True`` if the generation finished successfully."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """``True`` if the generation failed or was canceled."""
        return self.status in ("failed", "canceled")
