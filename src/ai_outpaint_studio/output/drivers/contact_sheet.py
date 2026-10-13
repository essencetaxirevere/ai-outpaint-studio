"""Builds a grid contact sheet from a batch of outpainted results."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from ai_outpaint_studio.config.loader import Config


class ContactSheetDriver:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def build(self, target_dir: Path, images: list[Path], thumb_px: int = 384) -> Path:
        thumbs: