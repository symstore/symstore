class FileFormatError(Exception):
    """
    raised on errors parsing various files
    """
    pass


class UnknownFileExtension(Exception):
    def __init__(self, file_extension):
        self.file_extension = file_extension
