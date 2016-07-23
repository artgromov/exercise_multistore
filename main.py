import logging
import sys
from exceptions import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)


class NotSet:
    """Placeholder for not set attributes"""
    pass


class NotDescribed:
    """Placeholder for not described attributes, that exists as dependencies"""
    pass


def dont_change(value):
    """Default formatter that doesnt change attribute and have no dependencies"""
    return value


class MultiStore:
    def __init__(self):
        self.tree = {}
        self.formatters = {}

    def build_tree(self):
        tree = {}
        for name, formatters in self.formatters.items():
            deps = set()
            for function in formatters:
                arg_names = function.__code__.co_varnames[1:function.__code__.co_argcount]  # 1 arg is for new value
                for arg in arg_names:
                    deps.add(arg)

            if name not in tree:
                tree[name] = set()

            for parent in deps:
                if parent in tree:
                    tree[parent].add(name)
                else:
                    tree[parent] = set(name)

        self.tree = tree

    def check_loop(self):
        try:
            self.get_recalc_order(*self.tree.keys())
        except RecursionError:
            raise LoopDependency

    def check_not_described(self):
        # check for attributes present in tree, but not exists
        for name in self.tree:
            if not hasattr(self, name):
                setattr(self, name, NotDescribed)

        # check for attributes not present in tree and NotDescribed
        attrs = dict(self.__dict__)
        for name, value in attrs.items():
            if value is NotDescribed:
                if name not in self.tree:
                    delattr(self, name)

    def get_subtree(self, *names):
        tree = self.tree
        subtree = {}

        def tree_walk(namelist):
            for parent in namelist:
                if parent in tree:
                    childs = set(tree[parent])  # copy to new set
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
            for parent in sorted(tree.keys()):
                if parent not in deps:
                    recalc_order.append(parent)
                    new_tree.pop(parent)

            if new_tree:
                tree_cut(new_tree)

        tree_cut(subtree)
        return recalc_order

    def describe(self, name, *formatters):
        if hasattr(type(self), name) or name == 'tree' or name == 'formatters':
            raise AttributeReserved
            
        setattr(self, name, NotSet)
        if len(formatters) == 0:
            # set default dont_change formatter
            formatters = (dont_change,)
        self.formatters[name] = formatters

        self.build_tree()
        self.check_loop()
        self.check_not_described()

    def remove(self, name):
        if hasattr(self, name):
            delattr(self, name)
            self.formatters.pop(name)

            self.build_tree()
            self.check_loop()
            self.check_not_described()

        else:
            raise AttributeNotExist

    def set(self, **kwargs):
        recalc_order = self.get_recalc_order(*list(kwargs.keys()))
        for number, name in enumerate(recalc_order):
            if name in kwargs:
                # use new value as start value
                new_value = kwargs[name]
                if name not in self.formatters:
                    # cannot continue, because attribute cannot be calculated
                    raise AttributeNotDescribed
            else:
                # use current value as start value
                new_value = getattr(self, name)
                if new_value is NotDescribed:
                    # make no change, will be checked as parent later if necessary
                    continue
                elif new_value is NotSet:
                    # make no change, will be checked as parent later if necessary
                    continue

            for function in self.formatters[name]:
                arg_names = function.__code__.co_varnames[1:function.__code__.co_argcount]  # skip 1st argument
                arg_dict = {}
                for arg in arg_names:
                    arg_value = getattr(self, arg)
                    if arg_value is NotSet:
                        raise ParentNotSet
                    elif arg_value is NotDescribed:
                        raise ParentNotDescribed
                    else:
                        arg_dict[arg] = arg_value

                new_value = function(new_value, **arg_dict)

            setattr(self, name, new_value)

    def get(self, name):
        if hasattr(self, name):
            value = getattr(self, name)
            if value is NotSet:
                raise AttributeNotSet
            if value is NotDescribed:
                raise AttributeNotDescribed
            return value
        else:
            raise AttributeNotExist
