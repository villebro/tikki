VERSION = (0, 9, 3)


def get_version() -> str:
    return '.'.join([str(v) for v in VERSION if v is not None])
