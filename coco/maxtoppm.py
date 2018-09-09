#!/usr/bin/env python
# encoding: utf-8
# maxtoppm - decoder for max and art graphics formats
# Original program "maxtoppm" written in Ruby
#   Copyright (c) 2018 by Mathieu Bouchard
# Translation to Python code:
#   Copyright (c) 2018 by Jamie Cho
#
# reads max art files and converts to ppm

from __future__ import division, print_function

import argparse
import sys

from util import getbit, pack


def convert(input_image_stream, output_image_stream, newsroom, width, height):
    pass


VERSION = '2018.09.08'
DESCRIPTION = """Convert RS-DOS MAX and ART images to PPM
Copyright (c) 2018 by Mathieu Bouchard, Jamie Cho
Version: {}""".format(VERSION)
PIXEL_MODE_DESCRIPTION = """Default pixel mode is no artifact (PMODE 4 on monitor). The 6 other modes:"""
PARSER_MODE_DESCRIPTION = """Default file format is CocoMax 1/2's .MAX, which is also Graphicom's
.PIC and SAVEM of 4 or 8 pages of PMODE 3/4.
Also works with any other height of SAVEM (including fractional pages)."""


def main():
    start(sys.argv[1:])


def start(argv):
    def check_positive(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
        return ivalue

    parser = argparse.ArgumentParser(description=DESCRIPTION,
      formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_image',
      metavar='image',
      type=argparse.FileType('rb'),
      nargs='?',
      default=sys.stdin,
      help='input image file')
    parser.add_argument('output_image',
      metavar='image.ppm',
      type=argparse.FileType('wb'),
      nargs='?',
      default=sys.stdout,
      help='output PPM image file')
    parser.add_argument('--version',
      action='version',
      version='%(prog)s {}'.format(VERSION))

    pixel_mode_group = parser.add_argument_group('pixel mode',
      description=PIXEL_MODE_DESCRIPTION)
    pixel_mode_parser = pixel_mode_group.add_mutually_exclusive_group()
    pixel_mode_parser.add_argument('-br',
      action='store_true',
      default=False,
      help='PMODE 4 artifacts, cyan-blue first')
    pixel_mode_parser.add_argument('-rb',
      action='store_true',
      default=False,
      help='PMODE 4 artifacts, orange-red first')
    pixel_mode_parser.add_argument('-br2',
      action='store_true',
      default=False,
      help='PMODE 3 Coco 3 cyan-blue first')
    pixel_mode_parser.add_argument('-rb2',
      action='store_true',
      default=False,
      help='PMODE 3 Coco 3 orange-red first')
    pixel_mode_parser.add_argument('-br3',
      action='store_true',
      default=False,
      help='PMODE 3 Coco 3 primary, blue first')
    pixel_mode_parser.add_argument('-rb3',
      action='store_true',
      default=False,
      help='PMODE 3 Coco 3 primary, red first')

    parser_mode_group = parser.add_argument_group('Format and size options:',
      description=PARSER_MODE_DESCRIPTION)
    parser_mode_group.add_argument('-i',
      action='store_true',
      default=False,
      help='ignore header errors (but read header anyway)')
    parser_mode_group.add_argument('-w',
      action='store',
      default=256,
      type=check_positive,
      help='choose different width (this does not assume bigger pixels)')
    parser_mode_group.add_argument('-newsroom',
      action='store_true',
      default=False,
      help='read Coco Newsroom / The Newspaper .ART header instead')

    args = parser.parse_args(argv)

    # convert(args.input_image, args.output_image)
    args.output_image.close()
    args.input_image.close()


if __name__ == '__main__':
    main()

