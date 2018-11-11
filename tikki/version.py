VERSION = (0, 9, 4)


def get_version() -> str:
    return '.'.join([str(v) for v in VERSION if v is not None])
