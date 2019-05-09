import logging

import s3fs
from tqdm.autonotebook import tqdm

from .paths import immutable_base
from .patterns import check_formats_compatible, get_fmt_match_dict, reformat


s3 = s3fs.S3FileSystem()
logger = logging.getLogger(__name__)


def copy(fmt_in, fmt_out, dryrun=True):
    fmt_in = fmt_in.lstrip("s3://")
    fmt_out = fmt_out.lstrip("s3://")
    if not check_formats_compatible(fmt_in, fmt_out):
        raise ValueError("Incompatible formats: %s -> %s", fmt_in, fmt_out)
    base_path = immutable_base(fmt_in)
    logger.info("Looking for objects on %s", base_path)
    candidate_files = s3.walk(base_path)
    logger.info("Trying %s objects", len(candidate_files))
    copied = 0
    for path_in in tqdm(candidate_files, total=len(candidate_files)):
        logger.debug("Trying %s ...", path_in)
        try:
            path_out = reformat(path_in, fmt_in, fmt_out)
            logger.debug("Copying %s to %s", path_in, path_out)
            if not dryrun:
                s3.copy_basic(path_in, path_out)
            copied += 1
        except (KeyError, TypeError):
            pass
    logger.info("Copied %s out of %s files", copied, len(candidate_files))
