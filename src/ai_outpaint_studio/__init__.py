"""ai-outpaint-studio — desktop AI image outpainting pipeline.

Public entrypoints live in :mod:`ai_outpaint_studio.cli` (CLI) and
:mod:`ai_outpaint_studio.app` (GUI bootstrap). Everything below is
composed of ingest handlers, processors, output drivers and job
utilities wired together by the pipeline runner.
"""

__version__ = "0.6.4"
__all__ = ["__version__"]