from exceptions import *


def is_number(value):
    if isinstance(value, int):
        return value
    else:
        raise InvalidValue('is not number')


class is_between:
    def __init__(self, minimum, maximum, strict=True):
        self.min = minimum
        self.max = maximum
        self.strict = strict

    def __call__(self, value):
        if self.strict:
            if value <= self.min:
                raise InvalidValue('le than min')
            elif self.max <= value:
                raise InvalidValue('ge than max')
            else:
                return value
        else:
            if value < self.min:
                raise InvalidValue('lt than min')
            elif self.max < value:
                raise InvalidValue('gt than max')
            else:
                return value
