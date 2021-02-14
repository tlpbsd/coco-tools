import os
import filecmp
import pkg_resources
import subprocess
import sys
import tempfile
import unittest

import coco.veftopng
from coco import __version__
from coco.util import iotostr


class TestVEFToPNG(unittest.TestCase):
    USAGE_REGEX = r'\[-h\] \[--version\] image.vef image.png'
    POSITIONAL_ARGS_REGEX = r'positional arguments:\s*image.vef\s*input VEF image file\s*' \
      r'image.png\s*output PNG image file'
    OPTIONAL_ARGS_REGEX = r'optional arguments:\s*-h, --help\s*show this help message and exit' \
      r'\s*--version\s*show program\'s version number and exit'
    VERSION_REGEX = r'{}'.format(__version__).replace('.', '\\.')

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile('w', suffix='.png', delete=False)

    def tearDown(self):
        if (not self.outfile.closed):
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_320x200x16_vef_to_png(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/trekies.vef')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/trekies.png')
        self.outfile.close()
        coco.veftopng.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_640x200x4_vef_to_png(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/owlcasl.vef')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/owlcasl.png')
        self.outfile.close()
        coco.veftopng.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/trekies.vef')
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              [sys.executable, 'src/coco/veftopng.py', infilename, self.outfile.name, 'baz'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(context.exception.output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(context.exception.output),
          r'veftopng.py: error: unrecognized arguments: baz')

    def test_help(self):
        output = subprocess.check_output([sys.executable, 'src/coco/veftopng.py', '-h'], stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(output), 'Convert OS-9 VEF images to PNG')
        self.assertRegexpMatches(iotostr(output), self.VERSION_REGEX)
        self.assertRegexpMatches(iotostr(output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(output), self.POSITIONAL_ARGS_REGEX)
        self.assertRegexpMatches(iotostr(output), self.OPTIONAL_ARGS_REGEX)

    def test_version(self):
        output = subprocess.check_output([sys.executable, 'src/coco/veftopng.py', '--version'],
          stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(output), self.VERSION_REGEX)

    def test_unknown_argument(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/trekies.vef')
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              [sys.executable, 'src/coco/veftopng.py', infilename, self.outfile.name, '--oops'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(context.exception.output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(context.exception.output),
          r'veftopng.py: error: unrecognized arguments: --oops')
