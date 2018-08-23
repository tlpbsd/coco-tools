import os
import filecmp
import pkg_resources
import subprocess
import tempfile
import unittest

import coco.mgetoppm


class TestCM3ToPPM(unittest.TestCase):
    USAGE_REGEX = r'\[-h\] \[--version\] \[image.mge\] \[image.ppm\]'
    POSITIONAL_ARGS_REGEX = r'positional arguments:\s*image.mge\s*input MGE image file\s*image.ppm\s*output PPM image file'
    OPTIONAL_ARGS_REGEX = r'optional arguments:\s*-h, --help\s*show this help message and exit\s*--version\s*show program\'s version number and exit'
    VERSION_REGEX = r'2018\.08\.20'

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile('w', suffix='.ppm', delete=False)

    def tearDown(self):
        if (not self.outfile.closed):
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_mge_to_ppm(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/dragon1.mge')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/dragon1.ppm')
        self.outfile.close()
        coco.mgetoppm.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/dragon1.mge')
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/mgetoppm.py', infilename, self.outfile.name, 'baz'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(context.exception.output, self.USAGE_REGEX)
        self.assertRegexpMatches(context.exception.output,
          r'mgetoppm.py: error: unrecognized arguments: baz')

    def test_converts_mge_to_ppm_via_stdio(self):
        infile = pkg_resources.resource_stream(__name__, 'fixtures/dragon1.mge')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/dragon1.ppm')
        subprocess.check_call(['coco/mgetoppm.py'], stdin=infile, stdout=self.outfile)
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_mge_to_ppm_via_stdin(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/dragon1.mge')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/dragon1.ppm')
        subprocess.check_call(['coco/mgetoppm.py', infilename], stdout=self.outfile)
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_help(self):
        output = subprocess.check_output(['coco/mgetoppm.py', '-h'], stderr=subprocess.STDOUT)
        self.assertRegexpMatches(output, 'Convert RS-DOS MGE images to PPM')
        self.assertRegexpMatches(output, self.VERSION_REGEX)
        self.assertRegexpMatches(output, self.USAGE_REGEX)
        self.assertRegexpMatches(output, self.POSITIONAL_ARGS_REGEX)
        self.assertRegexpMatches(output, self.OPTIONAL_ARGS_REGEX)

    def test_version(self):
        output = subprocess.check_output(['coco/mgetoppm.py', '--version'], stderr=subprocess.STDOUT)
        self.assertRegexpMatches(output, self.VERSION_REGEX)

    def test_unknown_argument(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/mgetoppm.py', '--oops'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(context.exception.output, self.USAGE_REGEX)
        self.assertRegexpMatches(context.exception.output,
          r'mgetoppm.py: error: unrecognized arguments: --oops')
