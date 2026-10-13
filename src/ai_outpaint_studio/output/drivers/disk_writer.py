"""Writes finalized outpainting results to the output directory."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from ai_outpaint_studio.config.loader import Config
from ai_outpaint_studio.models.job import OutpaintJob


class DiskWriter:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg

    def write(self, job: OutpaintJob, target_dir: Path) -> list[Path]:
        if job.result is None:
            raise RuntimeError("write called before a result exists")
        target_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = job.source_path.stem
        fname = f"{stem}_outpaint_{stamp}.{self.cfg.output.default_format}"
        out_path = target_dir / fname
        save_kwargs = {}
        if self.cfg.output.default_format.lower() == "png":
            save_kwargs["compress_level"] = self.cfg.output.png_compress_level
        job.result.save(out_path, **save_kwargs)
        logger.info("wrote {}", out_path)
        return [out_path]