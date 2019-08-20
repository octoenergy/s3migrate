import pytest

from s3migrate.patterns import (
    check_formats_compatible,
    fmt_string_to_regex_pattern,
    get_fmt_match_dict,
    reformat
)


@pytest.mark.parametrize(
    "fmt_string, regex",
    [
        ("key", "key"),
        ("bucket/key", "bucket/key"),
        ("{key_name}", "(?P<key_name>[^/]+)"),
        ("bucket/key={key}/{filename}", "bucket/key=(?P<key>[^/]+)/(?P<filename>[^/]+)"),
    ],
)
def test_fmt_string_to_regex_pattern(fmt_string, regex):
    regex_out = fmt_string_to_regex_pattern(fmt_string)
    assert regex_out == regex


@pytest.mark.parametrize(
    "fmt_string, string, fmt_dict",
    [
        ("key", "key", {}),
        ("bucket/key", "bucket2/key2", None),
        ("bucket/{key}", "bucket/value", {"key": "value"}),
        (
            "bucket/key={key}/{filename}",
            "bucket/key=123/part0.csv",
            {"key": "123", "filename": "part0.csv"},
        ),
        ("bucket/key={key}/{filename}", "bucket/key=123", None),
        ("bucket/key={key}/file.ext", "bucket/key=123/file.ext.backup", None),
    ],
)
def test_get_fmt_match_dict(fmt_string, string, fmt_dict):
    fmt_dict_out = get_fmt_match_dict(string, fmt_string)
    assert fmt_dict_out == fmt_dict


@pytest.mark.parametrize(
    "fmt1, fmt2, compat",
    [
        ("bucket", "bucket2", True),
        ("{key}/{filename}", "key={key}/filename={filename}", True),
        ("{key}/{filename}", "key={key}/filename", False),
        ("{key}", "key={key2}", False),
    ],
)
def test_check_formats_compatible(fmt1, fmt2, compat):
    compat_out = check_formats_compatible(fmt1, fmt2)
    assert compat_out == compat


@pytest.mark.parametrize(
    "fmt_in, fmt_out, string_in, string_out_expected",
    [
        (
            "{key}/{filename}",
            "key={key}/filename={filename}",
            "bucket/file.ext",
            "key=bucket/filename=file.ext",
        )
    ],
)
def test_reformat(fmt_in, fmt_out, string_in, string_out_expected):
    string_out = reformat(string_in, fmt_in, fmt_out)
    assert string_out == string_out_expected
