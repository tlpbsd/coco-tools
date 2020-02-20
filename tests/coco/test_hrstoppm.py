import os
import filecmp
import pkg_resources
import subprocess
import tempfile
import unittest

import coco.hrstoppm
from coco.util import iotostr


class TestHRSToPPM(unittest.TestCase):
    USAGE_REGEX = r'\[-h\] \[-w width\] \[-r height\] \[-s bytes\] \[--version\]\s*\[image.hrs\] \[image.ppm\]'
    POSITIONAL_ARGS_REGEX = r'positional arguments:\s*image.hrs\s*input HRS image file\s*' \
      r'image.ppm\s*output PPM image file'
    OPTIONAL_ARGS_REGEX = r'optional arguments:\s*-h, --help\s*show this help message and exit' \
      r'\s*-w width\s*choose different width \(this does not assume bigger pixels\)' \
      r'\s*-r height\s*choose height not computed from header divided by width' \
      r'\s*-s bytes\s*skip some number of bytes' \
      r'\s*--version\s*show program\'s version number and exit'
    VERSION_REGEX = r'2020\.03\.28'

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile('w', suffix='.ppm', delete=False)

    def tearDown(self):
        if (not self.outfile.closed):
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_hrs_to_ppm(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.hrs')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.ppm')
        self.outfile.close()
        coco.hrstoppm.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_hrs_to_ppm_with_height(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.hrs')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa_r97.ppm')
        self.outfile.close()
        coco.hrstoppm.start(['-r', '97', infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_hrs_to_ppm_with_width(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.hrs')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa_w160.ppm')
        self.outfile.close()
        coco.hrstoppm.start(['-w', '160', infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_skipping_bytes(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa_s7.hrs')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.ppm')
        self.outfile.close()
        coco.hrstoppm.start(['-s', '7', infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.hrs')
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/hrstoppm.py', infilename, self.outfile.name, 'baz'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(context.exception.output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(context.exception.output),
          r'hrstoppm.py: error: unrecognized arguments: baz')

    def test_converts_hrs_to_ppm_via_stdio(self):
        infile = pkg_resources.resource_stream(__name__, 'fixtures/monalisa.hrs')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.ppm')
        subprocess.check_call(['coco/hrstoppm.py'], stdin=infile, stdout=self.outfile)
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_hrs_to_ppm_via_stdin(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.hrs')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/monalisa.ppm')
        subprocess.check_call(['coco/hrstoppm.py', infilename], stdout=self.outfile)
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_help(self):
        output = subprocess.check_output(['coco/hrstoppm.py', '-h'], stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(output), 'Convert RS-DOS HRS images to PPM')
        self.assertRegexpMatches(iotostr(output), self.VERSION_REGEX)
        self.assertRegexpMatches(iotostr(output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(output), self.POSITIONAL_ARGS_REGEX)
        self.assertRegexpMatches(iotostr(output), self.OPTIONAL_ARGS_REGEX)

    def test_version(self):
        output = subprocess.check_output(['coco/hrstoppm.py', '--version'],
          stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(output), self.VERSION_REGEX)

    def test_unknown_argument(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/hrstoppm.py', '--oops'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(iotostr(context.exception.output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(context.exception.output),
          r'hrstoppm.py: error: unrecognized arguments: --oops')
