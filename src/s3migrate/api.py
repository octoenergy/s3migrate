import logging

import tentaclio as tio
from tqdm.autonotebook import tqdm

from .paths import immutable_base
from . import patterns


logger = logging.getLogger(__name__)


__all__ = ["cp", "copy", "mv", "move", "rm", "remove", "iter", "iterformats"]


def _yield_candidates(fmt_in):
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects in %s", base_path)
    for (dirpath, dirnames, filenames) in tio.fs.api.walk(base_path):  # FixMe: once tio is updated
        for filename in filenames:
            yield dirpath + filename


def copy(fmt_in, fmt_out, dryrun=True):
    fmt_in = fmt_in.lstrip("s3://")
    fmt_out = fmt_out.lstrip("s3://")
    if not patterns.check_formats_compatible(fmt_in, fmt_out):
        raise ValueError("Incompatible formats: %s -> %s", fmt_in, fmt_out)
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = _yield_candidates(fmt_in)
    total, copied = 0, 0
    for path_in in tqdm(candidate_files):
        logger.debug("Trying %s ...", path_in)
        total += 1
        try:
            path_out = patterns.reformat(path_in, fmt_in, fmt_out)
            logger.debug("Copying %s to %s", path_in, path_out)
            if not dryrun:
                s3.copy_basic(path_in, path_out)
            copied += 1
        except (KeyError, TypeError):
            pass
    logger.info("Copied %s out of %s files", copied, total)


def move(fmt_in, fmt_out, dryrun=True):
    fmt_in = fmt_in.lstrip("s3://")
    fmt_out = fmt_out.lstrip("s3://")
    if not patterns.check_formats_compatible(fmt_in, fmt_out):
        raise ValueError("Incompatible formats: %s -> %s", fmt_in, fmt_out)
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = _yield_candidates(fmt_in)
    total, moved = 0, 0
    for path_in in tqdm(candidate_files):
        logger.debug("Trying %s ...", path_in)
        total += 1
        try:
            path_out = patterns.reformat(path_in, fmt_in, fmt_out)
            logger.debug("Copying %s to %s", path_in, path_out)
            if not dryrun:
                s3.mv(path_in, path_out)
            moved += 1
        except (KeyError, TypeError):
            pass
    logger.info("Moved %s out of %s files", moved, total)


def remove(fmt_in, dryrun=True):
    candidate_files = _yield_candidates(fmt_in)
    total, removed = 0, 0
    for path_in in tqdm(candidate_files):
        total += 1
        if patterns.get_fmt_match_dict(path_in, fmt_in) is not None:
            logger.debug("Removing %s", path_in)
            if not dryrun:
                s3.rm(path_in)
            removed += 1
        else:
            pass
    logger.info("Removed %s out of %s files", removed, total)


cp = copy
mv = move
rm = remove


def iter(fmt_in):
    candidate_files = _yield_candidates(fmt_in)
    total, found = 0, 0
    for path_in in tqdm(candidate_files):
        total += 1
        if patterns.get_fmt_match_dict(path_in, fmt_in) is not None:
            yield path_in
            found += 1
        else:
            pass
    logger.info("Found %s out of %s files", found, total)


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
    logger.info("Found %s out of %s files", found, total)
