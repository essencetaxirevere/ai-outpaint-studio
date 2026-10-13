"""Orchestrates ingest -> processor -> output for an outpainting job."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from loguru import logger

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.handlers.file_ingest import FileIngestHandler
from ai_outpaint_studio.handlers.canvas_ingest import CanvasIngestHandler
from ai_outpaint_studio.models.job import OutpaintJob
from ai_outpaint_studio.pipeline.plan import build_plan
from ai_outpaint_studio.processors.diffusion_processor import DiffusionProcessor
from ai_outpaint_studio.processors.seam_blender import SeamBlender
from ai_outpaint_studio.services.model_registry import ModelRegistry
from ai_outpaint_studio.output.drivers.disk_writer import DiskWriter
from ai_outpaint_studio.output.drivers.sidecar_writer import SidecarWriter
from ai_outpaint_studio.output.drivers.contact_sheet import ContactSheetDriver
from ai_outpaint_studio.utils.tiling import parse_target


@dataclass
class _StageResult:
    job: OutpaintJob
    canvas_path: Path


class OutpaintRunner:
    """High-level entrypoint that the CLI and GUI both call into."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.registry = ModelRegistry(cfg.paths.model_root)
        self.file_ingest = FileIngestHandler(cfg)
        self.canvas_ingest = CanvasIngestHandler(cfg)
        self.processor = DiffusionProcessor(cfg, self.registry)
        self.blender = SeamBlender(cfg)
        self.disk_writer = DiskWriter(cfg)
        self.sidecar_writer = SidecarWriter(cfg)
        self.contact_sheet = ContactSheetDriver(cfg)

    def run(
        self,
        source: Path,
        target: str,
        anchor: str = "center",
        prompt: Optional[str] = None,
        negative: Optional[str] = None,
        steps: Optional[int] = None,
        guidance: Optional[float] = None,
        out_dir: Optional[Path] = None,
    ) -> list[Path]:
        width, height = parse_target(target)
        loaded = self.file_ingest.load(source)
        job = OutpaintJob(
            source_path=source,
            source_image=loaded.image,
            target_width=width,
            target_height=height,
            anchor=anchor,
            prompt=prompt,
            negative=negative,
            steps=steps or self.cfg.outpaint.default_steps,
            guidance=guidance or self.cfg.outpaint.default_guidance,
            seed=self.cfg.app.seed,
        )
        plan = build_plan(job, self.cfg)
        results: list[Path] = []
        for step in plan.steps:
            logger.debug("stage {}", step.name)
            if step.kind == "prep":
                self.canvas_ingest.prepare(job)
            elif step.kind == "diffuse":
                self.processor.process(job, step)
            elif step.kind == "blend":
                self.blender.blend(job)
        target_dir = out_dir or Path(self.cfg.paths.output_root)
        written = self.disk_writer.write(job, target_dir)
        results.extend(written)
        if self.cfg.output.write_sidecar_json:
            results.append(self.sidecar_writer.write(job, target_dir))
        if self.cfg.output.contact_sheet and len(written) > 1:
            results.append(self.contact_sheet.build(target_dir, written))
        return results

    def run_batch(self, jobs: Iterable[tuple[Path, str]]) -> list[Path]:
        out: list[Path] = []
        for src, tgt in jobs:
            out.extend(self.run(src, tgt))
        return out