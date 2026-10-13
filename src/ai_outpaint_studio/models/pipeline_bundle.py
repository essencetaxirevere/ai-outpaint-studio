"""A loaded diffusion bundle: pipe + controlnet + device + dtype."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch


@dataclass
class PipelineBundle:
    pipe: Any
    controlnet: Any
    device: torch.device
    dtype: torch.dtype
    name: str
    scheduler: str = "dpmpp_2m_karras"