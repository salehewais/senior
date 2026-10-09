import sys
from pathlib import Path


def import_commerce_erp():
    """Import the worker package shipped beside this addon.

    Compose sets PYTHONPATH to the package root. A checkout layout is
    services/odoo/src. The image mount is /opt/commerce_erp_src.
    """

    try:
        import commerce_erp
    except ImportError:
        candidates = (
            Path(__file__).resolve().parents[3] / "src",
            Path("/opt/commerce_erp_src"),
        )
        for candidate in candidates:
            if candidate.is_dir() and str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
        import commerce_erp
    return commerce_erp
