"""Console entry point for the TurtleBot3 RGB-D SDF patcher."""
from __future__ import annotations

from .sdf_patcher import main

__all__ = ["main"]


if __name__ == "__main__":
    raise SystemExit(main())
