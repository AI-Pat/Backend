class TokenExtractException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message


class TokenValidException(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message