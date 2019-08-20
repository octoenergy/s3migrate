import re


FMT_RE = "{([^/]+)}"
FMT_SUB = "(?P<\\1>[^/]+)"


def fmt_string_to_regex_pattern(fmt_string):
    return re.sub(FMT_RE, FMT_SUB, fmt_string)


def get_fmt_match_dict(string, fmt_string):
    regex = "^" + fmt_string_to_regex_pattern(fmt_string) + "$"
    match = re.match(regex, string)
    if not match:
        return None
    return match.groupdict()


def check_formats_compatible(fmt_in, fmt_out):
    keys_in = re.findall(FMT_RE, fmt_in)
    keys_out = re.findall(FMT_RE, fmt_out)
    return set(keys_in) == set(keys_out)


def reformat(string_in, fmt_in, fmt_out):
    fmt_dict = get_fmt_match_dict(string_in, fmt_in)
    return fmt_out.format(**fmt_dict)
