"""Prepares an outpainting canvas: build the target frame, place the source."""
from __future__ import annotations

from PIL import Image
from loguru import logger

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob
from ai_outpaint_studio.utils.masking import build_outpaint_mask


class CanvasIngestHandler:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def prepare(self, job: OutpaintJob) -> None:
        src = job.source_image
        tw, th = job.target_width, job.target_height
        canvas = Image.new("RGB", (tw, th), (0, 0, 0))
        paste_x, paste_y = self._anchor_offset(job)
        canvas.paste(src, (paste_x, paste_y))
        mask = build_outpaint_mask(
            (tw, th),
            (src.width, src.height),
            (paste_x, paste_y),
            feather=self.cfg.outpaint.feather_radius_px,
        )
        job.canvas = canvas
        job.mask = mask
        job.anchor_offset = (paste_x, paste_y)
        logger.debug("canvas prepared {}x{} anchor={}", tw, th, job.anchor)

    def _anchor_offset(self, job: OutpaintJob) -> tuple[int, int]:
        tw, th = job.target_width, job.target_height
        sw, sh = job.source_image.size
        if job.anchor == "left":
            return 0, (th - sh) // 2
        if job.anchor == "right":
            return tw - sw, (th - sh) // 2
        if job.anchor == "top":
            return (tw - sw) // 2, 0
        if job.anchor == "bottom":
            return (tw - sw) // 2, th - sh
        return (tw - sw) // 2, (th - sh) // 2