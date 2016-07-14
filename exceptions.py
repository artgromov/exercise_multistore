class MyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class InvalidValue(MyException):
    pass

