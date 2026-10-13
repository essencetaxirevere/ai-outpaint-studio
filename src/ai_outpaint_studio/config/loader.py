"""YAML config loader with pydantic validation and local overrides."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path("config/default.yaml")
LOCAL_CONFIG_PATH = Path("config/local.yaml")


class AppCfg(BaseModel):
    name: str = "ai-outpaint-studio"
    log_level: str = "INFO"
    device: str = "auto"
    dtype: str = "float16"
    seed: int = 6767


class PathsCfg(BaseModel):
    model_root: str = "models/weights"
    cache_root: str = "cache"
    output_root: str = "output"
    temp_root: str = "cache/tmp"


class IngestCfg(BaseModel):
    max_input_pixels: int = 4_194_304
    accepted_formats: list[str] = Field(default_factory=lambda: ["png", "jpg", "jpeg", "webp"])
    strip_exif: bool = True
    srgb_normalize: bool = True


class OutpaintCfg(BaseModel):
    base_model: str = "sd-xl-base-1.0"
    controlnet: str = "tile"
    default_steps: int = 28
    default_guidance: float = 6.5
    default_strength: float = 0.85
    scheduler: str = "dpmpp_2m_karras"
    tile_overlap_px: int = 64
    seam_blend: str = "cosine"
    feather_radius_px: int = 48


class OutputCfg(BaseModel):
    default_format: str = "png"
    png_compress_level: int = 6
    write_sidecar_json: bool = True
    contact_sheet: bool = True
    contact_sheet_cols: int = 4


class WorkersCfg(BaseModel):
    pool_size: int = 2
    prefetch_depth: int = 3
    retry_attempts: int = 2
    retry_backoff_sec: float = 3.0


class Config(BaseModel):
    app: AppCfg = AppCfg()
    paths: PathsCfg = PathsCfg()
    ingest: IngestCfg = IngestCfg()
    outpaint: OutpaintCfg = OutpaintCfg()
    output: OutputCfg = OutputCfg()
    workers: WorkersCfg = WorkersCfg()


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Optional[Path] = None) -> Config:
    """Load default.yaml, merge local.yaml (if present), then an explicit path."""
    data: dict = {}
    if DEFAULT_CONFIG_PATH.exists():
        data = yaml.safe_load(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    if LOCAL_CONFIG_PATH.exists():
        data = _merge(data, yaml.safe_load(LOCAL_CONFIG_PATH.read_text(encoding="utf-8")) or {})
    if path is not None:
        data = _merge(data, yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {})
    return Config.model_validate(data)