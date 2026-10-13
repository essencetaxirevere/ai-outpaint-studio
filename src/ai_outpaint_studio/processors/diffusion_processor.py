"""Runs the diffusion pass that paints the outpainted region."""
from __future__ import annotations

import torch
from loguru import logger

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob
from ai_outpaint_studio.models.pipeline_bundle import PipelineBundle
from ai_outpaint_studio.pipeline.plan import Step
from ai_outpaint_studio.services.model_registry import ModelRegistry
from ai_outpaint_studio.utils.device import pick_device, pick_dtype


class DiffusionProcessor:
    def __init__(self, cfg: Config, registry: ModelRegistry) -> None:
        self.cfg = cfg
        self.registry = registry
        self._bundle: PipelineBundle | None = None

    def _ensure_bundle(self) -> PipelineBundle:
        if self._bundle is None:
            device = pick_device(self.cfg.app.device)
            dtype = pick_dtype(self.cfg.app.dtype, device)
            self._bundle = self.registry.load_bundle(
                name=self.cfg.outpaint.base_model,
                controlnet=self.cfg.outpaint.controlnet,
                device=device,
                dtype=dtype,
            )
        return self._bundle

    def process(self, job: OutpaintJob, step: Step) -> None:
        bundle = self._ensure_bundle()
        generator = torch.Generator(device=bundle.device).manual_seed(job.seed)
        result = bundle.pipe(
            prompt=job.prompt or "",
            negative_prompt=job.negative or "",
            image=job.canvas,
            mask_image=job.mask,
            num_inference_steps=int(step.meta["steps"]),
            guidance_scale=float(step.meta["guidance"]),
            strength=float(step.meta["strength"]),
            generator=generator,
            output_type="pil",
        )
        job.result = result.images[0]
        logger.info("diffusion pass complete steps={}", step.meta["steps"])