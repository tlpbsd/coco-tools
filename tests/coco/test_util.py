import os
import filecmp
import pkg_resources
import subprocess
import tempfile
import unittest

import coco.veftopng

from coco.util import getbit, pack


class TestUtil(unittest.TestCase):
    def test_getbit(self):
        self.assertEqual(getbit(33, 0), 1)
        self.assertEqual(getbit(32, 0), 0)
        self.assertEqual(getbit(128, 7), 1)
        self.assertEqual(getbit(128, 0), 0)

    def test_pack(self):
        self.assertEqual(pack([65, 66, 255, 0]), 'AB\xff\x00')
