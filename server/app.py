"""OpenEnv server entry point for SecureReview.

This module re-exports the FastAPI app defined in ``app.main`` so the
environment is discoverable at the canonical ``server.app:app`` location
expected by ``openenv validate`` / ``openenv serve``. The ``main()``
function provides a direct-run entry point used by the ``[project.scripts]``
declaration in ``pyproject.toml``.
"""

from app.main import app

__all__ = ["app", "main"]


def main() -> None:
    """Run the SecureReview FastAPI server with uvicorn.

    Entry point for ``uv run --project . server`` and
    ``python -m server.app``.
    """
    import os
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
