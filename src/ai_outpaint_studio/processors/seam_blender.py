"""Blends the outpainted region back into the original for seamless seams."""
from __future__ import annotations

import numpy as np
from PIL import Image
from loguru import logger

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob
from ai_outpaint_studio.utils.masking import feather_alpha


class SeamBlender:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def blend(self, job: OutpaintJob) -> None:
        if job.result is None or job.mask is None:
            raise RuntimeError("blend called before diffuse produced a result")
        src = np.asarray(job.canvas, dtype=np.float32)
        gen = np.asarray(job.result, dtype=np.float32)
        alpha = feather_alpha(
            np.asarray(job.mask, dtype=np.float32),
            radius=self.cfg.outpaint.feather_radius_px,
        )[..., None]
        merged = src * (1.0 - alpha) + gen * alpha
        job.result = Image.fromarray(np.clip(merged, 0, 255).astype(np.uint8), "RGB")
        logger.debug("seam blend applied feather={}", self.cfg.outpaint.feather_radius_px)