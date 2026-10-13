"""Reads a manifest file listing (source, target, anchor) tuples."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator


def iter_manifest(path: Path) -> Iterator[tuple[Path, str, str]]:
    """Yield (source, target, anchor). CSV columns: source,target,anchor."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if header is None:
            return
        for row in reader:
            if len(row) < 2:
                continue
            source = Path(row[0]).expanduser()
            target = row[1].strip()
            anchor = row[2].strip() if len(row) > 2 else "center"
            yield source, target, anchor