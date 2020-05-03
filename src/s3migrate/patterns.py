import parse


def get_fmt_match_dict(string, fmt_string):
    parser = parse.compile(fmt_string)
    match = parser.parse(string)
    if not match:
        return None
    return match.named


def check_formats_compatible(fmt_in, fmt_out):
    parser_in = parse.compile(fmt_in)
    parser_out = parse.compile(fmt_out)
    return set(parser_in._named_fields) == set(parser_out._named_fields)


def reformat(string_in, fmt_in, fmt_out):
    fmt_dict = get_fmt_match_dict(string_in, fmt_in)
    return fmt_out.format(**fmt_dict)
