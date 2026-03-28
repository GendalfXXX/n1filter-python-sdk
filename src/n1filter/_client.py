"""Synchronous N1Filter API client.

Usage::

    from n1filter import N1FilterClient

    client = N1FilterClient("sk-your-api-key")
    balance = client.get_balance()

    # or as a context manager
    with N1FilterClient("sk-your-api-key") as client:
        order = client.generate_image("photo.jpg", preset="undress")
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Union

import httpx

from n1filter._base_client import BaseClient
from n1filter._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_WAIT,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_TIMEOUT,
    DOWNLOAD_TIMEOUT,
    PATH_BALANCE,
    PATH_DOWNLOAD,
    PATH_IMAGE,
    PATH_ORDER,
    PATH_ORDERS,
    PATH_PRICES,
    PATH_VIDEO,
)
from n1filter._enums import ImagePreset, VideoPreset
from n1filter._exceptions import DownloadError, TimeoutError
from n1filter._models import Balance, Order, Prices
from n1filter._types import FileInput


class N1FilterClient(BaseClient):
    """Synchronous client for the N1Filter Generation API.

    Uses :class:`httpx.Client` under the hood for HTTP/1.1 and HTTP/2
    connection pooling.

    The client can be used directly or as a context manager::

        # Direct usage
        client = N1FilterClient("sk-...")
        try:
            balance = client.get_balance()
        finally:
            client.close()

        # Context manager (recommended)
        with N1FilterClient("sk-...") as client:
            balance = client.get_balance()

    Args:
        api_key: Your N1Filter API key (format: ``sk-...``).
        base_url: Base URL of the N1Filter API.
        timeout: Default HTTP request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(api_key, base_url=base_url, timeout=timeout)
        self._http = httpx.Client(
            base_url=self._base_url,
            headers=self._headers,
            timeout=self._timeout,
        )

    def close(self) -> None:
        """Close the underlying HTTP client and release connections.

        Always call this method when you are done using the client, or use
        the client as a context manager to ensure automatic cleanup.
        """
        self._http.close()

    def __enter__(self) -> N1FilterClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── Core API ─────────────────────────────────────────────────────────

    def get_balance(self) -> Balance:
        """Get the current token balance.

        Returns:
            A :class:`~n1filter.Balance` object with the ``token_balance`` field.

        Raises:
            AuthenticationError: Invalid API key.
        """
        resp = self._http.get(PATH_BALANCE)
        body = resp.json()
        self._check_status(resp.status_code, body)
        return Balance.from_dict(body)

    def get_prices(self) -> Prices:
        """Get current pricing for all generation presets.

        Returns:
            A :class:`~n1filter.Prices` object containing image and video
            pricing with all available presets and their token costs.

        Raises:
            AuthenticationError: Invalid API key.
        """
        resp = self._http.get(PATH_PRICES)
        body = resp.json()
        self._check_status(resp.status_code, body)
        return Prices.from_dict(body)

    def generate_image(
        self,
        image: FileInput,
        preset: Union[str, ImagePreset],
    ) -> Order:
        """Submit an image generation request.

        Args:
            image: Source image — file path (``str`` / :class:`~pathlib.Path`),
                or raw ``bytes``. Allowed formats: JPEG, PNG, WebP. Max 5 MB.
            preset: Generation preset — a string or :class:`~n1filter.ImagePreset`
                enum value.

        Returns:
            An :class:`~n1filter.Order` with ``status="pending"`` and the
            assigned order ``id``.

        Raises:
            AuthenticationError: Invalid API key.
            InsufficientBalanceError: Not enough tokens.
            ValidationError: Bad file format/size or invalid preset.
            FileNotFoundError: Image file path does not exist.
        """
        filename, content, content_type = self._prepare_file(image)
        resp = self._http.post(
            PATH_IMAGE,
            files={"image": (filename, content, content_type)},
            data={"preset_id": str(preset)},
        )
        body = resp.json()
        self._check_status(resp.status_code, body)
        return Order.from_dict(body)

    def generate_video(
        self,
        image: FileInput,
        preset: Union[str, VideoPreset],
        *,
        seconds: int = 4,
    ) -> Order:
        """Submit a video generation request.

        Args:
            image: Source image — file path (``str`` / :class:`~pathlib.Path`),
                or raw ``bytes``. Allowed formats: JPEG, PNG, WebP. Max 5 MB.
            preset: Generation preset — a string or :class:`~n1filter.VideoPreset`
                enum value.
            seconds: Video duration in seconds. Must be between 4 and 8
                (inclusive). Defaults to 4.

        Returns:
            An :class:`~n1filter.Order` with ``status="pending"``.

        Raises:
            ValueError: *seconds* is not in the 4–8 range.
            AuthenticationError: Invalid API key.
            InsufficientBalanceError: Not enough tokens.
            ValidationError: Bad file format/size or invalid preset.
            FileNotFoundError: Image file path does not exist.
        """
        if not 4 <= seconds <= 8:
            raise ValueError(f"seconds must be between 4 and 8, got {seconds}")
        filename, content, content_type = self._prepare_file(image)
        resp = self._http.post(
            PATH_VIDEO,
            files={"image": (filename, content, content_type)},
            data={"preset_id": str(preset), "seconds": str(seconds)},
        )
        body = resp.json()
        self._check_status(resp.status_code, body)
        return Order.from_dict(body)

    def get_order(self, order_id: int) -> Order:
        """Get the current status of an order.

        Args:
            order_id: The order ID returned by :meth:`generate_image` or
                :meth:`generate_video`.

        Returns:
            An :class:`~n1filter.Order` with the latest status.

        Raises:
            NotFoundError: Order not found or does not belong to the user.
            AuthenticationError: Invalid API key.
        """
        resp = self._http.get(PATH_ORDER.format(order_id=order_id))
        body = resp.json()
        self._check_status(resp.status_code, body)
        return Order.from_dict(body)

    def list_orders(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:
        """List the user's generation orders.

        Args:
            limit: Number of orders to return (1–100). Defaults to 50.
            offset: Number of orders to skip (0–10 000). Defaults to 0.

        Returns:
            A list of :class:`~n1filter.Order` objects.

        Raises:
            AuthenticationError: Invalid API key.
            ValidationError: *limit* or *offset* out of range.
        """
        resp = self._http.get(
            PATH_ORDERS, params={"limit": limit, "offset": offset}
        )
        body = resp.json()
        self._check_status(resp.status_code, body)
        return [Order.from_dict(o) for o in body]

    # ── High-level helpers ───────────────────────────────────────────────

    def wait_for_result(
        self,
        order_id: int,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        max_wait: float = DEFAULT_MAX_WAIT,
    ) -> Order:
        """Poll an order until it reaches a terminal status.

        Calls :meth:`get_order` every *poll_interval* seconds until the
        order status becomes ``completed``, ``failed``, or ``canceled``.

        Args:
            order_id: The order ID to poll.
            poll_interval: Seconds between status checks. Defaults to 2.0.
            max_wait: Maximum total wait time in seconds. Defaults to 600.0
                (10 minutes).

        Returns:
            An :class:`~n1filter.Order` in a terminal state.

        Raises:
            TimeoutError: The order did not reach a terminal state within
                *max_wait* seconds. The exception carries ``order_id`` and
                ``last_status`` attributes.
            NotFoundError: Order not found.
            AuthenticationError: Invalid API key.
        """
        deadline = time.monotonic() + max_wait
        while True:
            order = self.get_order(order_id)
            if order.is_terminal:
                return order
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Order {order_id} did not complete within {max_wait}s "
                    f"(last status: {order.status})",
                    order_id=order_id,
                    last_status=order.status,
                )
            time.sleep(poll_interval)

    def download(
        self,
        order_id: int,
        save_to: Union[str, Path],
    ) -> Path:
        """Download the result of a completed order and save it to disk.

        Creates parent directories automatically if they do not exist.
        Uses a 120-second timeout to accommodate large video files.

        Args:
            order_id: ID of a completed order.
            save_to: Destination file path.

        Returns:
            :class:`~pathlib.Path` to the saved file.

        Raises:
            DownloadError: Empty response body.
            ValidationError: Order is not yet completed (HTTP 400).
            NotFoundError: Order not found.
            N1FilterError: Result has expired (HTTP 410).
        """
        save_path = Path(save_to)
        resp = self._http.get(
            PATH_DOWNLOAD.format(order_id=order_id),
            timeout=DOWNLOAD_TIMEOUT,
        )
        if resp.status_code != 200:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            self._check_status(resp.status_code, body)
        if len(resp.content) == 0:
            raise DownloadError("Received empty response body")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(resp.content)
        return save_path

    def download_bytes(self, order_id: int) -> bytes:
        """Download the result of a completed order as raw bytes.

        Useful when you want to process the result in memory (e.g. pass to
        PIL or a video processing library) without saving to disk.

        Uses a 120-second timeout to accommodate large video files.

        Args:
            order_id: ID of a completed order.

        Returns:
            Raw bytes of the result file.

        Raises:
            DownloadError: Empty response body.
            ValidationError: Order is not yet completed.
            NotFoundError: Order not found.
            N1FilterError: Result has expired (HTTP 410).
        """
        resp = self._http.get(
            PATH_DOWNLOAD.format(order_id=order_id),
            timeout=DOWNLOAD_TIMEOUT,
        )
        if resp.status_code != 200:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            self._check_status(resp.status_code, body)
        if len(resp.content) == 0:
            raise DownloadError("Received empty response body")
        return resp.content

    def generate_and_wait(
        self,
        image: FileInput,
        preset: str,
        *,
        type: str = "image",
        seconds: int = 4,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        max_wait: float = DEFAULT_MAX_WAIT,
    ) -> Order:
        """Generate and wait for the result in a single call.

        Convenience method that combines :meth:`generate_image` or
        :meth:`generate_video` with :meth:`wait_for_result`.

        Args:
            image: Source image (path, Path, or bytes).
            preset: Generation preset identifier.
            type: ``"image"`` or ``"video"``. Defaults to ``"image"``.
            seconds: Video duration (4–8), only used when *type* is
                ``"video"``. Defaults to 4.
            poll_interval: Seconds between status checks. Defaults to 2.0.
            max_wait: Maximum wait time in seconds. Defaults to 600.0.

        Returns:
            An :class:`~n1filter.Order` in a terminal state.

        Raises:
            ValueError: Invalid *type* value or *seconds* out of range.
            TimeoutError: Generation did not complete within *max_wait*.
            All exceptions from :meth:`generate_image` / :meth:`generate_video`.
        """
        if type == "image":
            order = self.generate_image(image, preset)
        elif type == "video":
            order = self.generate_video(image, preset, seconds=seconds)
        else:
            raise ValueError(f"type must be 'image' or 'video', got {type!r}")
        return self.wait_for_result(
            order.id,
            poll_interval=poll_interval,
            max_wait=max_wait,
        )
