import logging

import s3fs
from tqdm.autonotebook import tqdm

from .paths import immutable_base
from . import patterns


logger = logging.getLogger(__name__)


__all__ = ["cp", "copy", "mv", "move", "rm", "remove", "iter", "iterformats"]


FS = s3fs.S3FileSystem()
PROTOCOL = "s3"


def _yield_candidates(fmt_in):
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects in %s", base_path)
    for (dirpath, dirnames, filenames) in FS.walk(base_path):  # FixMe: once tio is updated
        for filename in filenames:
            yield PROTOCOL + "://" + dirpath + FS.sep + filename


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


def copy(fmt_in, fmt_out, dryrun=True):
    for fmt in iterformats(fmt_in):
        path_in = fmt_in.format(**fmt)
        path_out = fmt_out.format(**fmt)
        logger.debug("Copying %s to %s", path_in, path_out)
        if not dryrun:
            FS.copy_basic(path_in, path_out)


def move(fmt_in, fmt_out, dryrun=True):
    for fmt in iterformats(fmt_in):
        path_in = fmt_in.format(**fmt)
        path_out = fmt_out.format(**fmt)
        logger.debug("Moving %s to %s", path_in, path_out)
        if not dryrun:
            FS.move(path_in, path_out)


def remove(fmt_in, dryrun=True):
    for fmt in iterformats(fmt_in):
        path_in = fmt_in.format(**fmt)
        logger.debug("Removing %s", path_in)
        if not dryrun:
            FS.rm(path_in)


cp = copy
mv = move
rm = remove
