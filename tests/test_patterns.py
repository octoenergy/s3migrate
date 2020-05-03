import pytest

from s3migrate.patterns import check_formats_compatible, get_fmt_match_dict, reformat


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
        ("{key1}_{key2}", "12_34", {"key1": "12", "key2": "34"}),
        ("bucket/{file}.{ext}", "bucket/image.jpg", {"file": "image", "ext": "jpg"}),
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
        ("{key}_{key}", "key={key}", True),
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
        ),
        ("{key}_{key}.{ext}", "key={key}/ext={ext}", "img_img.jpg", "key=img/ext=jpg"),
    ],
)
def test_reformat(fmt_in, fmt_out, string_in, string_out_expected):
    string_out = reformat(string_in, fmt_in, fmt_out)
    assert string_out == string_out_expected
