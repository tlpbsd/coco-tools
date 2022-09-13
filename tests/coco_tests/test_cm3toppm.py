import os
import filecmp
import pkg_resources
import subprocess
import sys
import tempfile
import unittest

import coco.cm3toppm
from .util import unix_only
from coco import __version__
from coco.util import iotostr


class TestCM3ToPPM(unittest.TestCase):
    USAGE_REGEX = r"\[-h\] \[--version\] \[image.cm3\] \[image.ppm\]"
    POSITIONAL_ARGS_REGEX = (
        r"positional arguments:\s*image.cm3\s*input CM3 image file"
        r"\s*image.ppm\s*output PPM image file"
    )
    OPTIONAL_ARGS_REGEX = (
        r"option.*:\s*-h, --help\s*show this help message and exit"
        r"\s*--version\s*show program\'s version number and exit"
    )
    VERSION_REGEX = r"{}".format(__version__).replace(".", "\\.")

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile(
            "w", suffix=".ppm", delete=False
        )

    def tearDown(self):
        if not self.outfile.closed:
            self.outfile.close()
        os.remove(self.outfile.name)

    def test_converts_cm3_to_ppm(self):
        infilename = pkg_resources.resource_filename(
            __name__, "fixtures/clip1.cm3"
        )
        comparefilename = pkg_resources.resource_filename(
            __name__, "fixtures/clip1.ppm"
        )
        self.outfile.close()
        coco.cm3toppm.start([infilename, self.outfile.name])
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_too_many_arguments(self):
        infilename = pkg_resources.resource_filename(
            __name__, "fixtures/clip1.cm3"
        )
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
                [
                    sys.executable,
                    "src/coco/cm3toppm.py",
                    infilename,
                    self.outfile.name,
                    "baz",
                ],
                stderr=subprocess.STDOUT,
            )
        self.assertRegex(iotostr(context.exception.output), self.USAGE_REGEX)
        self.assertRegex(
            iotostr(context.exception.output),
            r"cm3toppm.py: error: unrecognized arguments: baz",
        )

    @unix_only
    def test_converts_cm3_to_ppm_via_stdio(self):
        infile = pkg_resources.resource_stream(__name__, "fixtures/clip1.cm3")
        comparefilename = pkg_resources.resource_filename(
            __name__, "fixtures/clip1.ppm"
        )
        read, write = os.pipe()
        os.write(write, infile.read())
        os.close(write)
        subprocess.check_call(
            [sys.executable, "src/coco/cm3toppm.py"],
            stdin=read,
            stdout=self.outfile,
        )
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_converts_cm3_to_ppm_via_stdin(self):
        infilename = pkg_resources.resource_filename(
            __name__, "fixtures/clip1.cm3"
        )
        comparefilename = pkg_resources.resource_filename(
            __name__, "fixtures/clip1.ppm"
        )
        subprocess.check_call(
            [sys.executable, "src/coco/cm3toppm.py", infilename],
            stdout=self.outfile,
        )
        self.assertTrue(filecmp.cmp(self.outfile.name, comparefilename))

    def test_help(self):
        output = subprocess.check_output(
            [sys.executable, "src/coco/cm3toppm.py", "-h"],
            stderr=subprocess.STDOUT,
        )
        self.assertRegex(iotostr(output), "Convert RS-DOS CM3 images to PPM")
        self.assertRegex(iotostr(output), self.VERSION_REGEX)
        self.assertRegex(iotostr(output), self.USAGE_REGEX)
        self.assertRegex(iotostr(output), self.POSITIONAL_ARGS_REGEX)
        self.assertRegex(iotostr(output), self.OPTIONAL_ARGS_REGEX)

    def test_version(self):
        output = subprocess.check_output(
            [sys.executable, "src/coco/cm3toppm.py", "--version"],
            stderr=subprocess.STDOUT,
        )
        self.assertRegex(iotostr(output), self.VERSION_REGEX)

    def test_unknown_argument(self):
        with self.assertRaises(subprocess.CalledProcessError) as context:
            subprocess.check_output(
                [sys.executable, "src/coco/cm3toppm.py", "--oops"],
                stderr=subprocess.STDOUT,
            )
        self.assertRegex(iotostr(context.exception.output), self.USAGE_REGEX)
        self.assertRegex(
            iotostr(context.exception.output),
            r"cm3toppm.py: error: unrecognized arguments: --oops",
        )
