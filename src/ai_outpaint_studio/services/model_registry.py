"""Loads and caches diffusion pipelines from the model root."""
from __future__ import annotations

from pathlib import Path

import torch
from loguru import logger

from ai_outpaint_studio.models.pipeline_bundle import PipelineBundle


class ModelRegistry:
    def __init__(self, model_root: str | Path) -> None:
        self.model_root = Path(model_root)
        self._cache: dict[str, PipelineBundle] = {}

    def load_bundle(
        self,
        name: str,
        controlnet: str | None,
        device: torch.device,
        dtype: torch.dtype,
    ) -> PipelineBundle:
        key = f"{name}|{controlnet or 'none'}|{device}|{dtype}"
        if key in self._cache:
            return self._cache[key]
        from diffusers import AutoPipelineForOutpainting, ControlNetModel

        cnet = None
        if controlnet:
            cnet = ControlNetModel.from_pretrained(
                f"lllyasviel/control_v11p_sd15_{controlnet}",
                torch_dtype=dtype,
            )
        pipe = AutoPipelineForOutpainting.from_pretrained(
            name, torch_dtype=dtype, controlnet=cnet
        ).to(device)
        bundle = PipelineBundle(pipe=pipe, controlnet=cnet, device=device, dtype=dtype, name=name)
        self._cache[key] = bundle
        logger.info("loaded bundle {}", key)
        return bundle

    def clear(self) -> None:
        self._cache.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()