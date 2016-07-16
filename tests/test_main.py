import unittest
import logging
import sys

from main import MultiStore
from exceptions import *


class TestAttribute(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()
        self.model.describe('a')
        self.model.describe('b')

    def test_setattr(self):
        self.model.a = 'a_value'
        self.assertEqual(self.model._a, 'a_value')

    def test_getattr(self):
        self.model._a = 'a_value'
        self.assertEqual(self.model.a, 'a_value')

    def test_getattr_notset(self):
        with self.assertRaises(AttributeNotSet):
            self.model.b

    def test_setget(self):
        self.model.a = 'a_value'
        self.assertEqual(self.model.a, 'a_value')


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
        def calc_b(a): pass
        def calc_c(a): pass
        def calc_d(a): pass
        def calc_e(b, c): pass
        def calc_f(b, c, e): pass
        def calc_g(b, c): pass
        def calc_h(f, g): pass

        with self.subTest('descibe, without loop'):
            self.model.describe('a')
            self.model.describe('b', calc_b)
            self.model.describe('c', calc_c)
            self.model.describe('d', calc_d)
            self.model.describe('e', calc_e)
            self.model.describe('f', calc_f)
            self.model.describe('g', calc_g)
            self.model.describe('h', calc_h)

            expected_tree = {'a': {'b', 'c', 'd'},
                             'b': {'e', 'f', 'g'},
                             'c': {'e', 'f', 'g'},
                             'd': set(),
                             'e': {'f'},
                             'f': {'h'},
                             'g': {'h'},
                             'h': set()
                             }

            self.assertDictEqual(self.model.tree, expected_tree)

        with self.subTest('describe, with loop'):
            with self.assertRaises(LoopDependency):
                self.model.describe('b', calc_f)

    def test_set(self):
        def calc_c(b):
            return 'c: "%s", b: "%s"' % (self, b)

        def calc_e(d):
            return 'e: "%s", d: "%s"' % (self, d)

        def calc_f(e):
            return 'f: "%s", e: %s' % (self, e)

        def calc_g(d):
            return 'g: "%s", d: %s' % (self, d)

        self.model.describe('a')
        self.model.describe('b')
        self.model.describe('c', calc_c)
        self.model.describe('d')
        self.model.describe('e', calc_e)
        self.model.describe('f', calc_f)
        self.model.describe('g', calc_g)

        with self.subTest('set attr with one dep'):
            self.model._c = 'c_value'
            self.model.set(b='b_value')
            self.assertEqual(self.model.b, 'b_value')
            self.assertEqual(self.model.c, 'c: "c_value", b: "b_value"')

        with self.subTest('set attr with one dep and dep is not set'):
            with self.assertRaises(AttributeNotSet):
                self.model.set(b='b_value')
                self.assertEqual(self.model.b, 'b_value')
                self.assertEqual(self.model.c, 'c: "c_value", b: "b_value"')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s',
                        stream=sys.stdout)

    unittest.main()
