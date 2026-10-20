"""DXF checks. A file must parse and contain geometry before it can reach the pattern team."""

import io

import ezdxf


def validate_dxf(text: str) -> list[str]:
    """Return a list of problems. An empty list means the file is valid."""
    try:
        doc = ezdxf.read(io.StringIO(text))
    except Exception as exc:  # ezdxf raises several error types for bad input
        return [f"unreadable DXF: {exc}"]

    errors: list[str] = []
    if len(doc.modelspace()) == 0:
        errors.append("no geometry in model space")
    return errors
