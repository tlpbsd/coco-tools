import argparse
import unittest

from coco.util import check_positive, check_zero_or_positive, getbit, pack


class TestUtil(unittest.TestCase):
    def test_check_positive(self):
        self.assertEqual(3, check_positive(3))
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive(0)
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive(-1)
        self.assertEqual(3, check_positive(3.9))

    def test_check_zero_or_positive(self):
        self.assertEqual(3, check_zero_or_positive(3))
        self.assertEqual(0, check_zero_or_positive(0))
        with self.assertRaises(argparse.ArgumentTypeError):
            check_positive(0)
        self.assertEqual(3, check_positive(3.9))

    def test_getbit(self):
        self.assertEqual(getbit(33, 0), 1)
        self.assertEqual(getbit(32, 0), 0)
        self.assertEqual(getbit(128, 7), 1)
        self.assertEqual(getbit(128, 0), 0)

    def test_pack(self):
        self.assertEqual(pack([65, 66, 255, 0]), 'AB\xff\x00')
