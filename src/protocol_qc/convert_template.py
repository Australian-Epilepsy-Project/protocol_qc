#!/usr/bin/env python3
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
Convert protocol_qc template JSON files from the pre-PR#42 format to the
format expected by the updated field-comparison parser.

Old format:
    "FieldName": {
        "value": <value>,
        "comparison": "<comparison_type>",
        ["compulsory": <bool>]
    }

New format:
    "FieldName": { "<comparison_type>": <value> }

Mapping of old comparison types to new:
    "exact"    (compulsory unset or true)  -> "exactly"
    "exact"    (compulsory: false)         -> "exactly_if_present"
    "regex"                                -> "regex"
    "absent"                               -> "absent"  (value: null)
    "in_set"                               -> "in_set"
    "in_range"                             -> "in_range"

The "options"-style entries inside "tags" blocks (where each option has a
"field" key and "comparison"/"value" keys) are also converted to the new
single-key format, consistent with how generate_tags.py now reads them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


_COMPARISON_RENAME: dict[str, str] = {
    "exact": "exactly",
    "regex": "regex",
    "absent": "absent",
    "in_set": "in_set",
    "in_range": "in_range",
}

# Tag option entries do not support "absent" or "compulsory".
_TAG_COMPARISON_RENAME: dict[str, str] = {
    "exact": "exactly",
    "regex": "regex",
    "in_set": "in_set",
    "in_range": "in_range",
}


def _convert_field_spec(field_name: str, spec: Any) -> Any:
    """
    Convert one entry from a ``fields`` dict.

    If ``spec`` is already in the new single-key format (no ``"comparison"``
    key present), it is returned unchanged.

    Parameters
    ----------
    field_name
        Name of the DICOM header field (used only for error messages).
    spec
        Value associated with ``field_name`` in a ``"fields"`` block.

    Returns
    -------
        Converted field specification.

    Raises
    ------
    KeyError
        If the old ``"comparison"`` value is not a recognised type.
    """
    if not isinstance(spec, dict) or "comparison" not in spec:
        return spec

    comparison: str = spec["comparison"]
    compulsory: bool = spec.get("compulsory", True)
    value: Any = spec.get("value", None)

    if comparison == "absent":
        return {"absent": None}

    if comparison not in _COMPARISON_RENAME:
        raise KeyError(
            f"Field \"{field_name}\": unrecognised comparison type \"{comparison}\""
        )

    new_key: str = _COMPARISON_RENAME[comparison]

    if comparison == "exact" and compulsory is False:
        new_key = "exactly_if_present"

    return {new_key: value}


def _convert_fields_block(fields: dict[str, Any]) -> dict[str, Any]:
    """
    Convert every entry in a ``"fields"`` block from old to new format.

    Parameters
    ----------
    fields
        The dict that is the value of a ``"fields"`` key.

    Returns
    -------
        Converted fields block.
    """
    return {name: _convert_field_spec(name, spec) for name, spec in fields.items()}


def _convert_tag_option(option_label: str, spec: Any) -> Any:
    """
    Convert one option entry inside an ``"options"``-style ``"tag"`` dict.

    If *spec* is already in the new single-key format (no ``"comparison"``
    key present), it is returned unchanged.

    Old format::

        {"field": "FieldName", "value": X, "comparison": "type"}

    New format::

        {"field": "FieldName", "type": X}

    Parameters
    ----------
    option_label
        The label for this option (used only in error messages).
    spec
        The dict describing one tag option.

    Returns
    -------
        Converted option dict.

    Raises
    ------
    KeyError
        If the ``"comparison"`` value is not a recognised type, or if
        ``"field"`` is missing.
    """
    if not isinstance(spec, dict) or "comparison" not in spec:
        return spec

    field: str = spec["field"]
    comparison: str = spec["comparison"]
    value: Any = spec.get("value", None)

    if comparison not in _TAG_COMPARISON_RENAME:
        raise KeyError(
            f"Tag option \"{option_label}\":"
            f" unrecognised comparison type \"{comparison}\""
        )

    return {"field": field, _TAG_COMPARISON_RENAME[comparison]: value}


def _convert_tags_block(tags: dict[str, Any]) -> dict[str, Any]:
    """
    Convert all ``"options"``-style tag entries within a ``"tags"`` block.

    Only entries whose ``"tag"`` value is a dict (the ``"options"`` pattern)
    contain field comparisons that need converting.  ``"constant"`` and
    ``"fill_with"`` entries are left unchanged.

    Parameters
    ----------
    tags
        The dict that is the value of a ``"tags"`` key.

    Returns
    -------
        Converted tags block.
    """
    result: dict[str, Any] = {}
    for tag_name, tag_spec in tags.items():
        if isinstance(tag_spec, dict) and isinstance(tag_spec.get("tag"), dict):
            new_options = {
                label: _convert_tag_option(label, opt)
                for label, opt in tag_spec["tag"].items()
            }
            result[tag_name] = {**tag_spec, "tag": new_options}
        else:
            result[tag_name] = tag_spec
    return result


def _convert_node(node: Any) -> Any:
    """
    Recursively convert all ``"fields"`` and ``"tags"`` blocks found in *node*.

    Parameters
    ----------
    node
        Any JSON-decoded Python object.

    Returns
    -------
        A new object with all ``"fields"`` and ``"tags"`` blocks converted.
    """
    if not isinstance(node, dict):
        return node

    result: dict[str, Any] = {}
    for key, value in node.items():
        if key == "tags" and isinstance(value, dict):
            result[key] = _convert_tags_block(value)
        elif key == "fields" and isinstance(value, dict):
            result[key] = _convert_fields_block(value)
        elif isinstance(value, dict):
            result[key] = _convert_node(value)
        elif isinstance(value, list):
            result[key] = [_convert_node(item) for item in value]
        else:
            result[key] = value

    return result


def convert_template(template: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a loaded protocol template from the old field-specification
    format to the new one.

    Parameters
    ----------
    template
        Python dict produced by ``json.load`` of a template file.

    Returns
    -------
        Converted template dict.
    """
    return _convert_node(template)


def _process_file(
    input_path: Path,
    output_path: Path | None,
    in_place: bool,
) -> None:
    """
    Load, convert and write a single template file.

    Parameters
    ----------
    input_path
        Path to the JSON template to read.
    output_path
        Explicit output path (``None`` when *in_place* is True or when
        using the default ``.new.json`` suffix).
    in_place
        If True, overwrite *input_path* with the converted content.
    """
    with input_path.open("r", encoding="utf-8") as fh:
        template: dict[str, Any] = json.load(fh)

    converted = convert_template(template)

    dest: Path
    if in_place:
        dest = input_path
    elif output_path is not None:
        dest = output_path
    else:
        dest = input_path.with_suffix("").with_suffix(".new.json")

    with dest.open("w", encoding="utf-8") as fh:
        json.dump(converted, fh, indent=2)
        fh.write("\n")

    print(f"Converted: {input_path} -> {dest}")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert protocol_qc template JSON files from the pre-PR#42 "
            "field-specification format to the updated format."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        metavar="PATH",
        help=(
            "One or more template JSON files (or directories containing them) "
            "to convert."
        ),
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--in-place",
        action="store_true",
        default=False,
        help=(
            "Overwrite each input file with the converted content. "
            "Cannot be used with --output."
        ),
    )
    mode.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        default=None,
        help=(
            "Write converted output to this path. "
            "Only valid when a single input file is given. "
            "Cannot be used with --in-place."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # Gather all JSON files from the provided inputs
    input_files: list[Path] = []
    for path in args.inputs:
        if not path.exists():
            print(f"ERROR: path does not exist: {path}", file=sys.stderr)
            return 1
        if path.is_dir():
            input_files.extend(sorted(path.glob("*.json")))
        elif path.suffix == ".json":
            input_files.append(path)
        else:
            print(f"ERROR: not a JSON file: {path}", file=sys.stderr)
            return 1

    if not input_files:
        print("ERROR: no JSON files found in the provided inputs.", file=sys.stderr)
        return 1

    if args.output is not None and len(input_files) > 1:
        print(
            "ERROR: --output can only be used with a single input file.",
            file=sys.stderr,
        )
        return 1

    for file in input_files:
        try:
            _process_file(file, args.output, args.in_place)
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            print(f"ERROR processing {file}: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
