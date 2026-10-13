"""Turns a job description into an ordered list of pipeline steps."""
from __future__ import annotations

from dataclasses import dataclass, field

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob


@dataclass
class Step:
    name: str
    kind: str  # prep | diffuse | blend
    meta: dict = field(default_factory=dict)


@dataclass
class Plan:
    steps: list[Step]


def build_plan(job: OutpaintJob, cfg: Config) -> Plan:
    steps = [
        Step(name="prep-canvas", kind="prep"),
        Step(
            name="diffuse-pass",
            kind="diffuse",
            meta={
                "steps": job.steps,
                "guidance": job.guidance,
                "strength": cfg.outpaint.default_strength,
                "scheduler": cfg.outpaint.scheduler,
            },
        ),
        Step(
            name="seam-blend",
            kind="blend",
            meta={
                "blend": cfg.outpaint.seam_blend,
                "feather": cfg.outpaint.feather_radius_px,
                "overlap": cfg.outpaint.tile_overlap_px,
            },
        ),
    ]
    return Plan(steps=steps)