# Package metadata and public exports
__version__ = "0.1.0"

# Expose the CLI entrypoint at package import time for convenience
from .main import cli  # noqa: F401

__all__ = ["cli", "__version__"]
