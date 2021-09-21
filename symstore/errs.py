class FileFormatError(Exception):
    """
    raised on errors parsing various files
    """
    pass


class UnknownFileType(Exception):
    pass


class FileNotFound(Exception):
    def __init__(self, filename):
        self.filename = filename


class TransactionNotFound(Exception):
    """
    raised when symstore does not contain transaction with specified ID
    """


class CabCompressionError(Exception):
    """
    raised on error creating CAB archive
    """
