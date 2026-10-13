"""Writes a JSON sidecar with the parameters used for each result."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob


class SidecarWriter:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def write(self, job: OutpaintJob, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        stem = job.source_path.stem
        out_path = target_dir / f"{stem}_outpaint.json"
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": str(job.source_path),
            "target": f"{job.target_width}x{job.target_height}",
            "anchor": job.anchor,
            "prompt": job.prompt,
            "negative": job.negative,
            "steps": job.steps,
            "guidance": job.guidance,
            "seed": job.seed,
            "base_model": self.cfg.outpaint.base_model,
            "scheduler": self.cfg.outpaint.scheduler,
            "seam_blend": self.cfg.outpaint.seam_blend,
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out_path