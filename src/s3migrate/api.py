import logging
from typing import Sequence, Union

import fsspec

from . import patterns


logger = logging.getLogger(__name__)


__all__ = ["ls", "list", "cp", "copy", "mv", "move", "rm", "remove", "iter", "iterformats"]


def _strip_prefix(path, prefix):
    """Strip prefix if matched exactly."""
    if path.startswith(prefix):
        path = path[len(prefix):]
    return path


def _get_fs_sep_prefix_paths(path: Union[str, Sequence[str]]):
    """Identify separator and prefix for various filesystems.

    In the case of local files, prefix is set to "" if original input path
    is not prefixed with the file:// prefix.
    """
    fs, _, paths = fsspec.get_fs_token_paths(path)
    protocol = fs.protocol
    if not isinstance(protocol, str):
        protocol, *_ = protocol
    prefix = protocol + "://"
    if isinstance(path, str):
        first_path = path
    else:
        first_path = path[0]
    if protocol == "file" and not first_path.startswith(prefix):  # local file notation
        prefix = ""
    try:
        sep = fs.pathsep
    except AttributeError:
        sep = "/"
    return fs, sep, prefix, paths


def _yield_candidates(path_fmt, fs=None, sep=None, prefix=None):
    if not fs:
        fs, sep, prefix, [path_fmt] = _get_fs_sep_prefix_paths(path_fmt)

    parts = path_fmt.split(sep)
    parts_immutable = ["{" not in part for part in parts]
    try:
        first_mutable = parts_immutable.index(False)
    except ValueError:  # path has no templates
        if fs.isfile(path_fmt):
            yield prefix + path_fmt
        return

    immutable_base = sep.join(parts[:first_mutable])
    this_fmt = sep.join(parts[: first_mutable + 1])
    remaining_fmt = sep.join(parts[first_mutable + 1:])
    if remaining_fmt:
        remaining_fmt = sep + remaining_fmt
    try:
        entries = fs.ls(immutable_base)
    except FileNotFoundError:
        return
    for entry in entries:
        fmt_dict = patterns.get_fmt_match_dict(entry.rstrip(sep), this_fmt)
        if fmt_dict is not None:
            yield from _yield_candidates(
                this_fmt.format(**fmt_dict) + remaining_fmt, fs=fs, sep=sep, prefix=prefix
            )


def iterformats(fmt_in):
    candidate_files = _yield_candidates(fmt_in)
    total, found = 0, 0
    for path_in in candidate_files:
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
    fs_in, sep, prefix_in, _ = _get_fs_sep_prefix_paths(fmt_in)
    fs_out, sep, prefix_out, _ = _get_fs_sep_prefix_paths(fmt_out)
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
    fs, _, prefix_in, _ = _get_fs_sep_prefix_paths(fmt_in)

    def rm(path_in):
        path_in = _strip_prefix(path_in, prefix_in)
        fs.rm(path_in)

    for fmt in iterformats(fmt_in):
        path_in = fmt_in.format(**fmt)
        logger.debug("Removing %s", path_in)
        if not dryrun:
            rm(path_in)


ls = list = iter
cp = copy
mv = move
rm = remove
