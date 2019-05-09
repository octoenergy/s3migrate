import pytest

from s3migrate.paths import immutable_base


@pytest.mark.parametrize(
    "path_fmt, base",
    [
        ("bucket", "bucket"),
        ("bucket/key", "bucket/key"),
        ("bucket/{key}", "bucket"),
        ("bucket/key={key}", "bucket"),
    ],
)
def test_fmt_string_to_regex_pattern(path_fmt, base):
    base_out = immutable_base(path_fmt)
    assert base_out == base
