"""Public type aliases for the N1Filter SDK."""

from __future__ import annotations

from os import PathLike
from typing import Union

FileInput = Union[str, "PathLike[str]", bytes]
"""Accepted image input types:

- ``str`` — file path
- ``PathLike`` — :class:`~pathlib.Path` or any path-like object
- ``bytes`` — raw image bytes (assumed JPEG)
"""
