import os
import filecmp
import pkg_resources
import subprocess
import tempfile
import unittest

import coco.maxtoppm


class TestMaxToPPM(unittest.TestCase):
    USAGE_REGEX = r'usage: maxtoppm \[-h\] \[--version\] \[-br | -rb | -br2 | -rb2 | -br3 | -rb3\] \[-i\]\n' \
                  r'\[-w width\] \[-newsroom\]' \
                  r'image\] \[image.ppm\]'
    POSITIONAL_ARGS_REGEX = r'positional arguments:\s*image\s*input image file\s*' \
      r'image.ppm\s*output PPM image file'
    OPTIONAL_ARGS_REGEX = r'optional arguments:\s*-h, --help\s*show this help message and exit' \
      r'\s*--version\s*show program\'s version number and exit'
    VERSION_REGEX = r'2018\.09\.08'

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile('w', suffix='.ppm', delete=False)

    def tearDown(self):
        if (not self.outfile.closed):
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_max_to_ppm(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_br(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_br.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-br'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_rb(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_br.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-br'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_br2(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_br2.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-br2'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_rb2(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_rb2.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-rb2'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_br3(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_br3.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-br3'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_rb3(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_rb3.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-rb3'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_specifying_width(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4_rb_w128.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-rb', '-w', '128'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_newsroom_files(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/shamrock.art')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/shamrock.ppm')
        self.outfile.close()
        coco.maxtoppm.start([infilename, self.outfile.name, '-newsroom'])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/maxtoppm.py', infilename, self.outfile.name, 'baz'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(context.exception.output, self.USAGE_REGEX)
        self.assertRegexpMatches(context.exception.output,
          r'maxtoppm.py: error: unrecognized arguments: baz')

    def test_converts_max_to_ppm_via_stdio(self):
        infile = pkg_resources.resource_stream(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.ppm')
        subprocess.check_call(['coco/maxtoppm.py'], stdin=infile, stdout=self.outfile)
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_max_to_ppm_via_stdin(self):
        infilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.max')
        comparefilename = pkg_resources.resource_filename(__name__, 'fixtures/eye4.ppm')
        subprocess.check_call(['coco/maxtoppm.py', infilename], stdout=self.outfile)
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_help(self):
        output = subprocess.check_output(['coco/maxtoppm.py', '-h'], stderr=subprocess.STDOUT)
        self.assertRegexpMatches(output, 'Convert RS-DOS MAX and ART images to PPM')
        self.assertRegexpMatches(output, self.VERSION_REGEX)
        self.assertRegexpMatches(output, self.USAGE_REGEX)
        self.assertRegexpMatches(output, self.POSITIONAL_ARGS_REGEX)
        self.assertRegexpMatches(output, self.OPTIONAL_ARGS_REGEX)

    def test_version(self):
        output = subprocess.check_output(['coco/maxtoppm.py', '--version'],
          stderr=subprocess.STDOUT)
        self.assertRegexpMatches(output, self.VERSION_REGEX)

    def test_unknown_argument(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
              ['coco/maxtoppm.py', '--oops'],
              stderr=subprocess.STDOUT)
        self.assertRegexpMatches(context.exception.output, self.USAGE_REGEX)
        self.assertRegexpMatches(context.exception.output,
          r'maxtoppm.py: error: unrecognized arguments: --oops')
