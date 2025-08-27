import re
from pathlib import Path


def filename_normalizer(filename: str) -> str:
    """Sanitize the filename by removing unsafe characters"""

    # remove leading/trailing whitespace and convert to lower case
    filename = filename.strip().lower()

    # if filename is empty, return a default name
    if not filename:
        return "unnamed_file"

    # extract name + extension
    file_name, ext = Path(filename).stem, Path(filename).suffix

    # replace unsafe characters with "_"
    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", file_name)

    return f"{safe_name}{ext}"
