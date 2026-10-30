"""`python -m legacy_documenter ...` -- same entry point as `python main.py ...` and the `legacymapper` console script."""
from legacy_documenter.main import main

if __name__ == "__main__":
    raise SystemExit(main())
