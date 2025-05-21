# protocol_qc: An MRI DICOM protocol quality control tool
# Copyright (C) 2025 The Florey Institute of Neuroscience and Mental Health

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Find the user defined protocol path_templates.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    import logging
    from pathlib import Path


def get_templates(
    path_templates: Path, logger: logging.Logger
) -> list[tuple[str, dict[str, Any]]]:
    """
    Find the user defined protocol path_templates.

    Parameters
    ----------
    path_templates:
        Path to template file or directory containing multiple template files.
    logger:
        Custom summary logger.

    Returns
    -------
        List of tuples containing template name and template.

    Raises
    ------
    FileNotFoundError
        If one or more template json files could not be located.
    """

    if not path_templates.exists():
        raise FileNotFoundError(
            f"Config file or directory does not exist: {path_templates}"
        )

    template_list = []
    if path_templates.is_file():
        if path_templates.suffix != ".json":
            raise FileNotFoundError("Input template is not a json file")
        logger.info(f"Using: {path_templates}")
        template_list.append(path_templates)
    else:
        for template in path_templates.glob("*.json"):
            template_list.append(template)

    templates: list[tuple[str, dict[str, Any]]] = []
    for template in template_list:
        with template.open("rb") as in_json:
            templates.append((template.name, json.load(in_json)))

    if not templates:
        raise FileNotFoundError("Input directory doesn't contain any json files")

    return templates
