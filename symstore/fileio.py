def read_all(fname, mode=None):
    """
    read all contents of a file
    """
    args = [fname]
    if mode is not None:
        args.append(mode)

    with open(*args) as f:
        return f.read()
