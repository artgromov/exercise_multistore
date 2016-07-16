import logging
import sys
from exceptions import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s: %(message)s',
                    stream=sys.stdout)


class NotSet:
    """Placeholder for not set attributes"""
    pass


def dont_change(value):
    """Formatter that doesnt change attribute and have no dependencies"""
    return value


class MultiStore:
    def __init__(self):
        self.tree = {}
        self.formatters = {}

    def describe(self, name, *formatters):
        if hasattr(self, name):
            self.remove(name)
            
        setattr(self, name, NotSet)
        if len(formatters) == 0:
            formatters = (dont_change,)
        self.formatters[name] = formatters

        deps = set()
        for function in formatters:
            arg_names = function.__code__.co_varnames[1:function.__code__.co_argcount]  # 1 arg is for new value
            for arg in arg_names:
                deps.add(arg)

        if name not in self.tree:
            self.tree[name] = set()

        for parent in deps:
            if parent == name:
                raise LoopDependency

            if parent in self.tree:
                self.tree[parent].add(name)
            else:
                self.tree[parent] = set(name)

    def remove(self, name):
        if hasattr(self, name):
            delattr(self, name)
            self.formatters.pop(name)
            self.tree.pop(name)
            for childs in self.tree.values():
                childs.remove(name)
                                
        else:
            raise AttributeNotDescribed
    
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

    def set(self, **kwargs):
        recalc_order = self.get_recalc_order(*list(kwargs.keys()))
        for number, name in enumerate(recalc_order):
            if name in kwargs:
                # use new value as start value
                new_value = kwargs[name]
            else:
                # use current value as start value
                new_value = getattr(self, name)
                if new_value is NotSet:
                    # make no change, check as parent later if needed
                    continue

            for function in self.formatters[name]:
                arg_names = function.__code__.co_varnames[1:function.__code__.co_argcount]  # skip 1st argument
                arg_dict = {}
                for arg in arg_names:
                    arg_value = getattr(self, arg)
                    if arg_value is NotSet:                    
                        raise ParentNotSet
                    else:
                        arg_dict[arg] = arg_value

                new_value = function(new_value, **arg_dict)

            setattr(self, name, new_value)

    def get(self, name):
        if hasattr(self, name):
            value = getattr(self, name)
            if value is NotSet:
                raise AttributeNotSet
        else:
            raise AttributeNotDescribed