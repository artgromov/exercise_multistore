from exceptions import *


class Attribute:
    def __init__(self, name, deps, functors, validators, default):
        self.name = '_' + name
        self.deps = ['_' + i for i in deps]
        self.functors = functors
        self.validators = validators
        self.default = default

    def __set__(self, instance, value):
        pass

    def __get__(self, instance, owner):
        if hasattr(instance, self.name):
            return getattr(instance, self.name)
        else:
            if self.default is None:
                raise AttributeError
            else:
                return self.default


class MultiStore:
    def __init__(self):
        pass

    @classmethod
    def describe(cls, name, deps=list(), functors=list(), validators=list(), default=None):
        descriptor = Attribute(name, deps, functors, validators, default)
        setattr(cls, name, descriptor)

    def set(self, **kwargs):
        pass

    def get(self, value):
        return getattr(self, value)

    def get_deptree(self, name):
        pass


if __name__ == '__main__':
    def is_number(value):
        if isinstance(value, int):
            return True
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
                    return True
            else:
                if value < self.min:
                    raise InvalidValue('lt than min')
                elif self.max < value:
                    raise InvalidValue('gt than max')
                else:
                    return True

    def quad_damage(value):
        return value * 4

    model = MultiStore()
    model.describe('a',
                   deps=['b', 'c'],
                   functors=[quad_damage],
                   validators=[is_number, is_between(1, 5)],
                   default=3)


