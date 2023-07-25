import pytest
from chatcmd.validators import validate_password, validate_username


@pytest.mark.parametrize(
    "input, expected",
    [("abc123!@#", True), ("abc", False), ("123", False), ("!@#", False)],
)
def test_password_validator(input, expected):
    assert validate_password(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [("gvard", True), ("gvard_123", True), ("gvard123", True), ("!@#", False)],
)
def test_name_validator(input, expected):
    assert validate_username(input) == expected
