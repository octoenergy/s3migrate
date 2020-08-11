import logging

import fsspec
from tqdm.autonotebook import tqdm

from . import patterns
from .paths import immutable_base


logger = logging.getLogger(__name__)


__all__ = ["cp", "copy", "mv", "move", "rm", "remove", "iter", "iterformats"]


def _strip_prefix(path, prefix):
    """Strip prefix if matched exactly."""
    if path.startswith(prefix):
        path = path[len(prefix):]
    return path


def _get_fs_sep_prefix(fmt_in):
    fs, _, _ = fsspec.get_fs_token_paths(fmt_in)
    protocol = fs.protocol
    if not isinstance(protocol, str):
        protocol, *_ = protocol
    prefix = protocol + "://"
    if protocol == "file" and not fmt_in.startswith(prefix):
        prefix = ""
    try:
        sep = fs.pathsep
    except AttributeError:
        sep = "/"
    return fs, sep, prefix


def _yield_candidates(fmt_in):
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects in %s", base_path)
    fs, sep, prefix = _get_fs_sep_prefix(fmt_in)
    for (dirpath, dirnames, filenames) in fs.walk(base_path):
        for filename in filenames:
            yield prefix + dirpath + sep + filename


def iterformats(fmt_in):
    candidate_files = _yield_candidates(fmt_in)
    total, found = 0, 0
    for path_in in tqdm(candidate_files):
        total += 1
        fmt_dict = patterns.get_fmt_match_dict(path_in, fmt_in)
        if fmt_dict is not None:
            yield fmt_dict
            found += 1
        else:
            pass
    logger.info("Matched %s out of %s files", found, total)


def iter(fmt_in):
    for fmt in iterformats(fmt_in):
        yield fmt_in.format(**fmt)


def _bin_op(fs_op_fn_getter, op_description: str, fmt_in, fmt_out, dryrun=True):
    """Shared functionality for move/copy."""
    fs_in, sep, prefix_in = _get_fs_sep_prefix(fmt_in)
    fs_out, sep, prefix_out = _get_fs_sep_prefix(fmt_out)
    if fs_out != fs_in:
        raise NotImplementedError("Can not copy between differen filesystems.")
    else:
        fs = fs_in
    _op_fn = fs_op_fn_getter(fs)

    def op_fn(path_in, path_out, prefix_in=prefix_in, prefix_out=prefix_out):
        path_in = _strip_prefix(path_in, prefix_in)
        path_out = _strip_prefix(path_out, prefix_out)
        _op_fn(path_in, path_out)

    for fmt in iterformats(fmt_in):
        path_in = fmt_in.format(**fmt)
        path_out = fmt_out.format(**fmt)
        logger.debug(f"{op_description} %s to %s", path_in, path_out)
        if not dryrun:
            path_out_dir_only = sep.join(path_out.split(sep)[:-1])
            fs.makedirs(path_out_dir_only, exist_ok=True)
            op_fn(path_in, path_out)


def copy(fmt_in, fmt_out, dryrun=True):
    """Copy files to new parametrised locations."""

    def _copy_fn_getter(fs):
        try:
            _copy_fn = fs.copy_basic
        except AttributeError:
            _copy_fn = fs.copy
        return _copy_fn

    return _bin_op(
        fs_op_fn_getter=_copy_fn_getter,
        op_description="Copying",
        fmt_in=fmt_in,
        fmt_out=fmt_out,
        dryrun=dryrun,
    )


def move(fmt_in, fmt_out, dryrun=True):
    """Move files to new parametrised locations."""

    def _move_fn_getter(fs):
        return fs.move

    return _bin_op(
        fs_op_fn_getter=_move_fn_getter,
        op_description="Moving",
        fmt_in=fmt_in,
        fmt_out=fmt_out,
        dryrun=dryrun,
    )


def remove(fmt_in, dryrun=True):
    fs, _, prefix_in = _get_fs_sep_prefix(fmt_in)

    def rm(path_in):
        path_in = _strip_prefix(path_in, prefix_in)
        fs.rm(path_in)

    for fmt in iterformats(fmt_in):
        path_in = fmt_in.format(**fmt)
        logger.debug("Removing %s", path_in)
        if not dryrun:
            rm(path_in)


cp = copy
mv = move
rm = remove
