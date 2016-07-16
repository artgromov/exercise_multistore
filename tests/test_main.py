import unittest
import logging
import sys

from main import *
from exceptions import *


class TestMultiStore(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()

    def test_get_subtree(self):
        self.model.tree = {'a': {'b', 'c', 'd'},
                           'b': {'e', 'f', 'g'},
                           'c': {'e', 'f', 'g'},
                           'd': set(),
                           'e': {'f'},
                           'f': {'h'},
                           'g': {'h'},
                           'h': set()
                           }

        subtree = self.model.get_subtree('c', 'd')
        expected_tree = {'c': {'e', 'f', 'g'},
                         'd': set(),
                         'e': {'f'},
                         'f': {'h'},
                         'g': {'h'},
                         'h': set()
                         }

        self.assertDictEqual(subtree, expected_tree)

    def test_get_recalc_order(self):
        self.model.tree = {'a': {'b', 'c', 'd'},
                           'b': {'e', 'f', 'g'},
                           'c': {'e', 'f', 'g'},
                           'd': set(),
                           'e': {'f'},
                           'f': {'h'},
                           'g': {'h'},
                           'h': set()
                           }

        recalc_order = self.model.get_recalc_order('c', 'd')
        expected_list = ['c', 'd', 'e', 'g', 'f', 'h']

        self.assertListEqual(recalc_order, expected_list)

    def test_describe(self):
        def mutate(value): pass
        def mutate_with_dep(value, a): pass
        def calc_b(value, a): pass
        def calc_c(value, a): pass
        def calc_d(value, a): pass
        def calc_e(value, b, c): pass
        def calc_f(value, b, c, e): pass
        def calc_g(value, b, c): pass
        def calc_h(value, f, g): pass
        def calc_k(value, k): pass

        self.model.describe('a')
        self.model.describe('b', calc_b)
        self.model.describe('c', calc_c)
        self.model.describe('d', calc_d, mutate)
        self.model.describe('e', mutate, calc_e)
        self.model.describe('f', calc_f, mutate_with_dep)
        self.model.describe('g', calc_g)
        self.model.describe('h', calc_h)

        with self.subTest('check tree'):
            expected_tree = {'a': {'b', 'c', 'd', 'f'},
                             'b': {'e', 'f', 'g'},
                             'c': {'e', 'f', 'g'},
                             'd': set(),
                             'e': {'f'},
                             'f': {'h'},
                             'g': {'h'},
                             'h': set()
                             }

            self.assertDictEqual(self.model.tree, expected_tree)

        with self.subTest('check formatters stack'):
            expected_formatters = {'a': (dont_change,),
                                   'b': (calc_b,),
                                   'c': (calc_c,),
                                   'd': (calc_d, mutate),
                                   'e': (mutate, calc_e),
                                   'f': (calc_f, mutate_with_dep),
                                   'g': (calc_g,),
                                   'h': (calc_h,)
                                   }

            self.assertDictEqual(self.model.formatters, expected_formatters)

        with self.subTest('check raise when loop'):
            with self.assertRaises(LoopDependency):
                self.model.describe('k', calc_k)


class TestMultiStoreSet(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()

        def mutate(value): return 'mutate(%s)' % value
        def calc_d(value, c): return 'calc_d(%s, %s)' % (value, c)
        def calc_f(value, e): return 'calc_f(%s, %s)' % (value, e)
        def calc_g(value, e): return 'calc_g(%s, %s)' % (value, e)
        def calc_h(value, g): return 'calc_h(%s, %s)' % (value, g)

        self.model.describe('a')
        self.model.describe('b', mutate)
        self.model.describe('c')
        self.model.describe('d', calc_d)
        self.model.describe('e')
        self.model.describe('f', calc_f)
        self.model.describe('g', calc_g, mutate)
        self.model.describe('h', mutate, calc_h)

    def test_without_deps_without_change(self):
        self.model.set(a='a')
        self.assertEqual(self.model.a, 'a')

    def test_without_deps_with_change(self):
        self.model.set(b='b')
        self.assertEqual(self.model.b, 'mutate(b)')

    def test_with_child(self):
        self.model.set(c='c', d='d')
        self.assertEqual(self.model.d, 'calc_d(d, c)')

    def test_with_child_notset(self):
        self.model.set(c='c')
        self.assertEqual(self.model.c, 'c')
        self.assertIs(self.model.d, NotSet)

    def test_with_child_recalc(self):
        self.model.set(c='c', d='d')
        self.model.set(c='c')
        self.assertEqual(self.model.d, 'calc_d(calc_d(d, c), c)')

    def test_with_parent_notset(self):
        with self.assertRaises(ParentNotSet):
            self.model.set(d='d')
    @unittest.skip
    def test_complex(self):
        self.model.set


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s',
                        stream=sys.stdout)

    unittest.main()
