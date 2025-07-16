#User defined exceptions

class PageException(Exception):
    def __init__(self, message):
        super().__init__(message)

class IdInUseException(Exception):
    def __init__(self, message):
        super().__init__(message)