import s3migrate


def test_iterformats(file_tree):
    base_url, files = file_tree
    pattern = base_url + "/{ds}/type={type}/{filename}.ext"
    for idx_found, fmt in enumerate(s3migrate.iterformats(pattern)):
        assert pattern.format(**fmt) in files
    assert idx_found + 1 == len(files)
