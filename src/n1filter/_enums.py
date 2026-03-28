"""Enumerations for presets and order statuses.

All enums inherit from ``str``, so they can be used as plain string values
wherever a preset or status string is expected.
"""

from enum import Enum


class ImagePreset(str, Enum):
    """Available presets for image generation."""

    UNDRESS = "undress"
    SHIBARI_HARNESS = "shibari_harness"
    BDSM_SINGLE = "bdsm_single"
    COWGIRL = "cowgirl"
    BLOWJOB_POV = "blowjob_pov"
    DOGGYSTYLE_VAGINAL = "doggystyle_vaginal"


class VideoPreset(str, Enum):
    """Available presets for video generation."""

    UNDRESS = "undress"
    FINGER_MASTURBATION = "finger_masturbation"
    AHEGAO = "ahegao"
    BLOWJOB = "blowjob"
    BLOWJOB_POV = "blowjob_pov"
    DOGGYSTYLE_VAGINAL = "doggystyle_vaginal"
    MISSIONARY = "missionary"
    COWGIRL = "cowgirl"
    REVERSE_COWGIRL = "reverse_cowgirl"
    TITJOB = "titjob"


class OrderStatus(str, Enum):
    """Possible statuses of a generation order."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
