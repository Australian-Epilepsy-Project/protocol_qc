"""
Tests for parser.py
"""

import pytest

from protocol_qc.utils import parser


@pytest.mark.parametrize(
    "inputs,error_message",
    [
        ([], "error: the following arguments are required"),
        (["arg1", "arg2", "arg3"], "unrecognized arguments: arg3"),
        (["arg1", "arg2", "--arg3"], "unrecognized arguments: --arg3"),
    ],
)
def test_parser_fail(capsys, inputs, error_message):
    """Test parser with no args"""

    with pytest.raises(SystemExit):
        _ = parser.parse_args(inputs)

    captured = capsys.readouterr()
    assert error_message in captured.err
