import os
import filecmp
import pkg_resources
import sys
import subprocess
import tempfile
import unittest

import coco.pixtopgm
from coco import __version__
from coco.util import iotostr


class TestPixToPGM(unittest.TestCase):
    USAGE_REGEX = r"\[-h\] \[--version\] image.pix \[image.pgm\]"
    POSITIONAL_ARGS_REGEX = (
        r"positional arguments:\s*image.pix\s*input PIX image file\s*"
        r"image.pgm\s*output PGM image file"
    )
    OPTIONAL_ARGS_REGEX = (
        r"optional arguments:\s*-h, --help\s*show this help message and exit"
        r"\s*--version\s*show program\'s version number and exit"
    )
    VERSION_REGEX = r"{}".format(__version__).replace(".", "\\.")

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile(
            "w", suffix=".pgm", delete=False
        )

    def tearDown(self):
        if not self.outfile.closed:
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_pix_to_pgm(self):
        infilename = pkg_resources.resource_filename(
            __name__, "fixtures/sue.pix"
        )
        comparefilename = pkg_resources.resource_filename(
            __name__, "fixtures/sue.pgm"
        )
        self.outfile.close()
        coco.pixtopgm.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        infilename = pkg_resources.resource_filename(
            __name__, "fixtures/sue.pix"
        )
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
                [
                    sys.executable,
                    "src/coco/pixtopgm.py",
                    infilename,
                    self.outfile.name,
                    "baz",
                ],
                stderr=subprocess.STDOUT,
            )
        self.assertRegexpMatches(
            iotostr(context.exception.output), self.USAGE_REGEX
        )
        self.assertRegexpMatches(
            iotostr(context.exception.output),
            r"pixtopgm.py: error: unrecognized arguments: baz",
        )

    def test_converts_pix_to_pgm_via_stdout(self):
        infile = pkg_resources.resource_filename(__name__, "fixtures/sue.pix")
        comparefilename = pkg_resources.resource_filename(
            __name__, "fixtures/sue.pgm"
        )
        subprocess.check_call(
            [sys.executable, "src/coco/pixtopgm.py", infile],
            stdout=self.outfile,
        )
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_help(self):
        output = subprocess.check_output(
            [sys.executable, "src/coco/pixtopgm.py", "-h"],
            stderr=subprocess.STDOUT,
        )
        self.assertRegexpMatches(
            iotostr(output), "Convert RS-DOS PIX images to PGM"
        )
        self.assertRegexpMatches(iotostr(output), self.VERSION_REGEX)
        self.assertRegexpMatches(iotostr(output), self.USAGE_REGEX)
        self.assertRegexpMatches(iotostr(output), self.POSITIONAL_ARGS_REGEX)
        self.assertRegexpMatches(iotostr(output), self.OPTIONAL_ARGS_REGEX)

    def test_version(self):
        output = subprocess.check_output(
            [sys.executable, "src/coco/pixtopgm.py", "--version"],
            stderr=subprocess.STDOUT,
        )
        self.assertRegexpMatches(iotostr(output), self.VERSION_REGEX)

    def test_unknown_argument(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            infile = pkg_resources.resource_filename(
                __name__, "fixtures/sue.pix"
            )
            subprocess.check_output(
                [sys.executable, "src/coco/pixtopgm.py", infile, "--oops"],
                stderr=subprocess.STDOUT,
            )
        self.assertRegexpMatches(
            iotostr(context.exception.output), self.USAGE_REGEX
        )
        self.assertRegexpMatches(
            iotostr(context.exception.output),
            r"pixtopgm.py: error: unrecognized arguments: --oops",
        )
