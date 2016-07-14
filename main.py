from exceptions import *


class Attribute:
    def __init__(self, name, functors, validators):
        self.name = name
        self.local_name = '_' + name
        self.functors = functors
        self.validators = validators

    def __set__(self, instance, value):
        pass

    def __get__(self, instance, owner):
        if hasattr(instance, self.local_name):
            return getattr(instance, self.local_name)
        else:
            raise AttributeNotSet(self.name)


class MultiStore:
    def __init__(self):
        self.tree = {}

    def describe(self, name, deps=list(), functors=list(), validators=list()):
        descriptor = Attribute(name, functors, validators)
        setattr(self.__class__, name, descriptor)
        for parent in deps:
            if parent in self.tree:
                self.tree[parent].add(name)
            else:
                self.tree[parent] = set(name)

    def remove(self):
        pass

    def get_subtree(self, *names):
        tree = self.tree
        subtree = {}

        def tree_walk(namelist):
            for parent in namelist:
                if parent in tree:
                    childs = set(tree[parent])
                    if parent not in subtree:
                        subtree[parent] = childs
                    tree_walk(childs)

        tree_walk(names)
        return subtree

    def get_recalc_order(self, *names):
        subtree = self.get_subtree(*names)
        recalc_order = []

        def tree_cut(tree):
            deps = set()
            for value in tree.values():
                deps.update(value)
            new_tree = dict(tree)
            for parent in tree:
                if parent not in deps:
                    recalc_order.append(parent)
                    childs = new_tree.pop(parent)

                    new_deps = set()
                    for value in new_tree.values():
                        new_deps.update(value)
                    for child in childs:
                        if child not in tree and child not in new_deps:
                            recalc_order.append(child)
            if new_tree:
                tree_cut(new_tree)

        tree_cut(subtree)
        return recalc_order

    def set(self, **kwargs):
        pass

    def get(self, value):
        return getattr(self, value)


def dget(name):
    return MultiStore.__dict__[name]


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
    model.describe('1')
    model.describe('a', deps=['1'])
    model.describe('b', deps=['1'])
    model.describe('c', deps=['a', 'b'])
    model.describe('d', deps=['c', 'a'])
    model.describe('e', deps=['c', 'b', 'd'])
    model.describe('f', deps=['b'])
    model.describe('g', deps=['1'])

    print(model.get_subtree('g', 'f', 'c'))
    print(model.get_recalc_order('g', 'f', 'c'))
