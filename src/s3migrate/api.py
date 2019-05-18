import logging

import s3fs
from tqdm.autonotebook import tqdm

from .paths import immutable_base
from . import patterns


s3 = s3fs.S3FileSystem()
logger = logging.getLogger(__name__)


__all__ = ["cp", "copy", "mv", "move", "rm", "remove", "iter", "iterformats"]


def copy(fmt_in, fmt_out, dryrun=True):
    fmt_in = fmt_in.lstrip("s3://")
    fmt_out = fmt_out.lstrip("s3://")
    if not patterns.check_formats_compatible(fmt_in, fmt_out):
        raise ValueError("Incompatible formats: %s -> %s", fmt_in, fmt_out)
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = s3.walk(base_path)
    logger.info("Trying %s objects", len(candidate_files))
    copied = 0
    for path_in in tqdm(candidate_files, total=len(candidate_files)):
        logger.debug("Trying %s ...", path_in)
        try:
            path_out = patterns.reformat(path_in, fmt_in, fmt_out)
            logger.debug("Copying %s to %s", path_in, path_out)
            if not dryrun:
                s3.copy_basic(path_in, path_out)
            copied += 1
        except (KeyError, TypeError):
            pass
    logger.info("Copied %s out of %s files", copied, len(candidate_files))


def move(fmt_in, fmt_out, dryrun=True):
    fmt_in = fmt_in.lstrip("s3://")
    fmt_out = fmt_out.lstrip("s3://")
    if not patterns.check_formats_compatible(fmt_in, fmt_out):
        raise ValueError("Incompatible formats: %s -> %s", fmt_in, fmt_out)
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = s3.walk(base_path)
    logger.info("Trying %s objects", len(candidate_files))
    moved = 0
    for path_in in tqdm(candidate_files, total=len(candidate_files)):
        logger.debug("Trying %s ...", path_in)
        try:
            path_out = patterns.reformat(path_in, fmt_in, fmt_out)
            logger.debug("Copying %s to %s", path_in, path_out)
            if not dryrun:
                s3.mv(path_in, path_out)
            moved += 1
        except (KeyError, TypeError):
            pass
    logger.info("Moved %s out of %s files", moved, len(candidate_files))


def remove(fmt_in, dryrun=True):
    fmt_in = fmt_in.lstrip("s3://")
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = s3.walk(base_path)
    logger.info("Trying %s objects", len(candidate_files))
    removed = 0
    for path_in in tqdm(candidate_files, total=len(candidate_files)):
        if patterns.get_fmt_match_dict(path_in, fmt_in) is not None:
            logger.debug("Removing %s", path_in)
            if not dryrun:
                s3.rm(path_in)
            removed += 1
        else:
            pass
    logger.info("Removed %s out of %s files", removed, len(candidate_files))


cp = copy
mv = move
rm = remove


def iter(fmt_in):
    fmt_in = fmt_in.lstrip("s3://")
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = s3.walk(base_path)
    logger.info("Trying %s objects", len(candidate_files))
    found = 0
    for path_in in tqdm(candidate_files, total=len(candidate_files)):
        if patterns.get_fmt_match_dict(path_in, fmt_in) is not None:
            yield path_in
            found += 1
        else:
            pass
    logger.info("Found %s out of %s files", found, len(candidate_files))


def iterformats(fmt_in):
    fmt_in = fmt_in.lstrip("s3://")
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = s3.walk(base_path)
    logger.info("Trying %s objects", len(candidate_files))
    found = 0
    for path_in in tqdm(candidate_files, total=len(candidate_files)):
        fmt_dict = patterns.get_fmt_match_dict(path_in, fmt_in)
        if fmt_dict is not None:
            yield fmt_dict
            found += 1
        else:
            pass
    logger.info("Found %s out of %s files", found, len(candidate_files))
