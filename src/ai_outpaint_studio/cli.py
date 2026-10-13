"""Command-line entrypoint for ai-outpaint-studio."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from ai_outpaint_studio.config.loader import load_config
from ai_outpaint_studio.pipeline.runner import OutpaintRunner
from ai_outpaint_studio.utils.logging_setup import configure_logging

app = typer.Typer(
    name="outpaint",
    help="Extend an image beyond its frame with diffusion-guided outpainting.",
    no_args_is_help=True,
)


@app.command()
def run(
    image: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    target: str = typer.Option("2048x1152", help="Target canvas, e.g. 2048x1152"),
    anchor: str = typer.Option("center", help="center|left|right|top|bottom"),
    prompt: Optional[str] = typer.Option(None, help="Optional style prompt"),
    negative: Optional[str] = typer.Option(None, help="Optional negative prompt"),
    steps: Optional[int] = typer.Option(None, help="Override sampler steps"),
    guidance: Optional[float] = typer.Option(None, help="Override CFG scale"),
    out: Optional[Path] = typer.Option(None, help="Output directory override"),
    config: Optional[Path] = typer.Option(None, help="Path to a YAML config"),
) -> None:
    """Outpaint IMAGE to a TARGET canvas and write results to OUT."""
    cfg = load_config(config)
    configure_logging(cfg.app.log_level)
    logger.info("outpaint start image={} target={}", image, target)
    runner = OutpaintRunner(cfg)
    results = runner.run(
        source=image,
        target=target,
        anchor=anchor,
        prompt=prompt,
        negative=negative,
        steps=steps,
        guidance=guidance,
        out_dir=out,
    )
    for r in results:
        logger.info("wrote {}", r)


if __name__ == "__main__":
    sys.exit(app())