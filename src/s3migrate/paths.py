def immutable_base(path_fmt):
    parts = path_fmt.split("/")
    parts_immutable = ["{" not in part for part in parts]
    try:
        first_mutable = parts_immutable.index(False)
    except ValueError:
        first_mutable = len(parts)
    return "/".join(parts[:first_mutable])
