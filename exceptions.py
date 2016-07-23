class AttributeCustomError(Exception):
    pass


class AttributeReserved(AttributeCustomError):
    pass


class AttributeNotExist(AttributeCustomError):
    pass


class AttributeNotDescribed(AttributeCustomError):
    pass


class AttributeNotSet(AttributeCustomError):
    pass


class ParentNotSet(AttributeNotSet):
    pass


class ParentNotDescribed(AttributeNotDescribed):
    pass


class InvalidValue(AttributeCustomError):
    pass


class LoopDependency(AttributeCustomError):
    pass

