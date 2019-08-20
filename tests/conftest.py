import pytest
from pytest_lazyfixture import lazy_fixture

import moto
import boto3

import tentaclio as tio


@pytest.fixture
def s3_writable_url():
    """Returns a writable S3 URL."""
    test_bucket_name = "test_bucket"
    with moto.mock_s3():
        client = boto3.client("s3")
        client.create_bucket(Bucket=test_bucket_name)
        url = f"s3://{test_bucket_name}"
        yield url


@pytest.fixture
def local_writable_url(tmp_path):
    """Return a writable local URL."""
    path = str(tmp_path)
    url = f"file://{path}"
    yield url


TREE = [
    "2018-01-01/type=one/file.ext",
    "2018-01-02/type=two/file.ext",
    "2018-01-03/type=three/file1.ext",
    "2018-01-03/type=three/file2.ext",
]


@pytest.fixture(
    params=[
        lazy_fixture("s3_writable_url"),
        # lazy_fixture("local_writable_url")
    ]
)
def file_tree(request):
    base_url = request.param
    tree = [base_url + "/" + sub_path for sub_path in TREE]
    for file_url in tree:
        with tio.open(file_url, "w") as f:
            f.write("bla")
    return base_url, tree
