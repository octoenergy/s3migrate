import s3migrate


def test_yield_candidates(file_tree):
    """Test that pruning is done early."""
    base_url, files = file_tree
    pattern = base_url + "/{ds}/type=three/{filename}.ext"
    candidates = list(s3migrate.api._yield_candidates(pattern))
    assert len(candidates) == 2


def test_iterformats(file_tree):
    base_url, files = file_tree
    pattern = base_url + "/{ds}/type={type}/{filename}.ext"
    for idx_found, fmt in enumerate(s3migrate.iterformats(pattern)):
        assert pattern.format(**fmt) in files
    assert idx_found + 1 == len(files)


def test_copy(file_tree):
    base_url, files = file_tree
    fmt_in = base_url + "/{ds}/type={type}/{filename}.ext"
    fmt_out = base_url + "/year={ds}/{filename}.{type}"

    s3migrate.copy(fmt_in, fmt_out, dryrun=False)

    new_files = list(s3migrate.iter(fmt_out))
    assert len(new_files) == len(files)


def test_move(file_tree):
    base_url, files = file_tree
    fmt_in = base_url + "/{ds}/type={type}/{filename}.ext"
    fmt_out = base_url + "/year={ds}/{filename}.{type}"

    s3migrate.move(fmt_in, fmt_out, dryrun=False)

    old_files = list(s3migrate.iter(fmt_in))
    new_files = list(s3migrate.iter(fmt_out))
    assert len(old_files) == 0
    assert len(new_files) == len(files)


def test_remove(file_tree):
    base_url, files = file_tree
    fmt_in = base_url + "/{ds}/type={type}/{filename}.ext"

    s3migrate.remove(fmt_in, dryrun=False)

    old_files = list(s3migrate.iter(fmt_in))
    assert len(old_files) == 0
