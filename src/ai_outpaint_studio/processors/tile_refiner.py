"""Optional post-pass: refine seams by re-diffusing overlapping tiles."""
from __future__ import annotations

from PIL import Image
from loguru import logger

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob


class TileRefiner:
    """Refines each outpainted tile with a small local diffusion pass.

    Currently a no-op scaffold — wired so the plan can call it without
    changing the pipeline shape when the real refinement kernel lands.
    """

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def refine(self, job: OutpaintJob) -> Image.Image:
        logger.debug("tile refiner skipped (scaffold)")
        if job.result is None:
            raise RuntimeError("refine called before a result exists")
        return job.result