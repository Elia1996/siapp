import io
from typing import Tuple


def path_to_bytes(path: str) -> Tuple[str, bytes]:
    """Convert a file to bytes

    Args:
        path (str): Path to the file

    Returns:
        List[str, bytes]: Tuple with the extension of the file
            and the file in bytes
    """
    ext = path.split(".")[-1]
    with open(path, "rb") as f:
        return ext, io.BytesIO(f.read()).getvalue()
