#
# Copyright (c) 2024 Elia Ribaldone.
#
# This file is part of SiApp 
# (see https://github.com/Elia1996/siapp).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.#
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
