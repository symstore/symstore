class FileFormatError(Exception):
    """
    raised on errors parsing various files
    """
    pass


class UnknownFileExtension(Exception):
    def __init__(self, file_extension):
        self.file_extension = file_extension


class FileNotFound(Exception):
    def __init__(self, filename):
        self.filename = filename


class TransactionNotFound(Exception):
    """
    raised when symstore does not contain transaction with specified ID
    """
