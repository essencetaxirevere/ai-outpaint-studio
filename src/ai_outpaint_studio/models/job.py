"""The mutable job object threaded through every pipeline stage."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PIL import Image


@dataclass
class OutpaintJob:
    source_path: Path
    source_image: Image.Image
    target_width: int
    target_height: int
    anchor: str = "center"
    prompt: Optional[str] = None
    negative: Optional[str] = None
    steps: int = 28
    guidance: float = 6.5
    seed: int = 6767

    canvas: Optional[Image.Image] = None
    mask: Optional[Image.Image] = None
    result: Optional[Image.Image] = None
    anchor_offset: tuple[int, int] = (0, 0)
    metadata: dict = field(default_factory=dict)

    def describe(self) -> str:
        return (
            f"OutpaintJob(src={self.source_path.name}, "
            f"target={self.target_width}x{self.target_height}, anchor={self.anchor})"
        )