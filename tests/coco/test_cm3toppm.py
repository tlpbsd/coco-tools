import os
import filecmp
import pkg_resources
import subprocess
import tempfile
import unittest

import coco.cm3toppm


class TestCM3ToPPM(unittest.TestCase):
    USAGE_REGEX = r'\[-h\] \[--version\] [image.cm3] [image.ppm]'

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile('w', suffix='.ppm', delete=False)

    def tearDown(self):
        if (not self.outfile.closed):
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_cm3_to_ppm(self):
        inputfilename = pkg_resources.resource_filename(__name__, 'fixtures/clip1.cm3')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/clip1.ppm')
        self.outfile.close()
        coco.cm3toppm.start([inputfilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        inputfilename = pkg_resources.resource_filename(__name__, 'fixtures/clip1.cm3')
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/cm3toppm.py', 'foo', 'bar', 'baz'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(context.exception.output, self.USAGE_REGEX)
        self.assertRegexpMatches(context.exception.output,
          r'cm3toppm.py: error: unrecognized arguments: baz')
