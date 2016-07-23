import unittest

from main import *
from exceptions import *


def mutate(value): return 'mutate(%s)' % value
def from_a(value, a): return 'from_a(%s,%s)' % (value, a)
def from_b(value, b): return 'from_b(%s,%s)' % (value, b)
def from_c(value, c): return 'from_c(%s,%s)' % (value, c)
def from_d(value, d): return 'from_d(%s,%s)' % (value, d)
def from_e(value, e): return 'from_e(%s,%s)' % (value, e)
def from_f(value, f): return 'from_f(%s,%s)' % (value, f)
def from_g(value, g): return 'from_g(%s,%s)' % (value, g)
def from_h(value, h): return 'from_h(%s,%s)' % (value, h)
def from_k(value, k): return 'from_k(%s,%s)' % (value, k)
def from_h_k(value, h, k): return 'from_h_k(%s, %s, %s)' % (value, h, k)
def from_b_c(value, b, c): pass
def from_b_e(value, b, e): pass
def from_f_g(value, f, g): pass


class TestTreeMethods(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()

    def test_build_tree(self):
        self.model.formatters = {'a': (dont_change,),
                                 'b': (from_a,),
                                 'c': (from_a,),
                                 'd': (from_a, mutate),
                                 'e': (mutate, from_b_c),
                                 'f': (from_b_e, from_c),
                                 'g': (from_b_c,),
                                 'h': (from_f_g,)
                                 }

        expected_tree = {'a': {'b', 'c', 'd'},
                         'b': {'e', 'f', 'g'},
                         'c': {'e', 'f', 'g'},
                         'd': set(),
                         'e': {'f'},
                         'f': {'h'},
                         'g': {'h'},
                         'h': set()
                         }

        self.model.build_tree()
        self.assertDictEqual(self.model.tree, expected_tree)

    def test_check_loop(self):
        with self.subTest('check simple loop'):
            with self.assertRaises(LoopDependency):
                self.model.formatters['a'] = (from_a,)
                self.model.build_tree()

        with self.subTest('check indirect loop'):
            pass

    def test_check_not_described_in_tree(self):
        self.model.tree = {'a': set()}
        self.model.check_not_described()
        self.assertIs(self.model.a, NotDescribed)

    def test_check_not_described_not_in_tree(self):
        self.model.a = NotDescribed
        self.model.check_not_described()
        self.assertFalse(hasattr(self.model, 'a'))

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

        expected_subtree = {'c': {'e', 'f', 'g'},
                            'd': set(),
                            'e': {'f'},
                            'f': {'h'},
                            'g': {'h'},
                            'h': set()
                            }

        subtree = self.model.get_subtree('c', 'd')

        self.assertDictEqual(subtree, expected_subtree)

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

        expected_list = ['c', 'd', 'e', 'g', 'f', 'h']

        recalc_order = self.model.get_recalc_order('c', 'd')

        self.assertListEqual(recalc_order, expected_list)


class TestAttributeMethods(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()

        self.model.describe('a')
        self.model.describe('b', from_a)
        self.model.describe('c', from_a)
        self.model.describe('d', from_a, mutate)
        self.model.describe('e', mutate, from_b_c)
        self.model.describe('f', from_b_e, from_c)
        self.model.describe('g', from_b_c)
        self.model.describe('h', from_f_g)

    def test_describe(self):
        with self.subTest('check formatters stack'):
            expected_formatters = {'a': (dont_change,),
                                   'b': (from_a,),
                                   'c': (from_a,),
                                   'd': (from_a, mutate),
                                   'e': (mutate, from_b_c),
                                   'f': (from_b_e, from_c),
                                   'g': (from_b_c,),
                                   'h': (from_f_g,)
                                   }

            self.assertDictEqual(self.model.formatters, expected_formatters)

        with self.subTest('check attribute'):
            self.assertIs(self.model.f, NotSet)

        with self.subTest('check reserved object name'):
            with self.assertRaises(AttributeReserved):
                self.model.describe('tree')

        with self.subTest('check reserved class name'):
            with self.assertRaises(AttributeReserved):
                self.model.describe('describe')

    def test_remove(self):
        # deleting attribute without child is by desire
        # logic that checks dependencies on tree change is in check_not_described method
        self.model.remove('h')

        with self.subTest('check formatters stack'):
            expected_formatters = {'a': (dont_change,),
                                   'b': (from_a,),
                                   'c': (from_a,),
                                   'd': (from_a, mutate),
                                   'e': (mutate, from_b_c),
                                   'f': (from_b_e, from_c),
                                   'g': (from_b_c,),
                                   }

            self.assertDictEqual(self.model.formatters, expected_formatters)

        with self.subTest('check attribute'):
            self.assertFalse(hasattr(self.model, 'h'))

        with self.subTest('check not exist name'):
            with self.assertRaises(AttributeNotExist):
                self.model.remove('blabla')

    def test_remove_describe(self):
        expected_formatters = {'a': (dont_change,),
                               'b': (from_a,),
                               'c': (from_a,),
                               'd': (from_a, mutate),
                               'e': (mutate, from_b_c),
                               'f': (from_b_e, from_c),
                               'g': (from_b_c,),
                               'h': (from_f_g,)
                               }

        self.model.remove('f')
        self.model.remove('h')

        self.model.describe('f', from_b_e, from_c)
        self.model.describe('h', from_f_g)

        # should get the same formatters that was on start
        self.assertDictEqual(self.model.formatters, expected_formatters)


class TestSetMethod(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()

        self.model.describe('a')
        self.model.describe('b', from_a)
        self.model.describe('c')
        self.model.describe('d', mutate, from_c)
        self.model.describe('e', from_d, mutate)

    def test_independent(self):
        self.model.set(a='a')
        self.assertEqual(self.model.a, 'a')

    def test_dependent(self):
        self.model.a = 'a'
        self.model.set(b='b')
        self.assertEqual(self.model.b, 'from_a(b,a)')

    def test_dependent_recalc(self):
        self.model.a = 'a'
        self.model.b = 'b'
        self.model.set(a='_a')
        self.assertEqual(self.model.b, 'from_a(b,_a)')

    def test_attribute_not_described(self):
        self.model.remove('a')
        with self.assertRaises(AttributeNotDescribed):
            self.model.set(a='a')

    def test_parent_not_set(self):
        with self.assertRaises(ParentNotSet):
            self.model.set(b='b')

    def test_parent_not_described(self):
        self.model.remove('a')
        with self.assertRaises(ParentNotDescribed):
            self.model.set(b='b')

    def test_complex(self):
        self.model.c = 'c'
        self.model.d = 'd'
        self.model.e = 'e'
        self.model.set(c='_c')
        self.assertEqual(self.model.e, 'mutate(from_d(e,from_c(mutate(d),_c)))')
        # c = _c
        # d = from_c(mutate(d),_c)
        # e = mutate(from_d(e,from_c(mutate(d),_c)))


class TestGetMethod(unittest.TestCase):
    def setUp(self):
        self.model = MultiStore()
        self.model.describe('a')
        self.model.describe('b', from_a)
        self.model.a = 'a'

    def test_get(self):
        value = self.model.get('a')
        self.assertEqual(value, 'a')

    def test_get_not_set(self):
        with self.assertRaises(AttributeNotSet):
            self.model.get('b')

    def test_get_not_described(self):
        self.model.remove('a')
        with self.assertRaises(AttributeNotDescribed):
            self.model.get('a')

    def test_get_not_exist(self):
        with self.assertRaises(AttributeNotExist):
            self.model.get('c')


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(message)s',
                        stream=sys.stdout)  # to sync printed output

    unittest.main()
