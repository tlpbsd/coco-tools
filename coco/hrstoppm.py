#!/usr/bin/env python
# encoding: utf-8
# hrstoppm - decoder for hrs (Davinci 3) format
# Original program "hrstoppm" written in Ruby
#   Copyright (c) 2018 by Mathieu Bouchard
# Translation to Python code:
#   Copyright (c) 2018 by Jamie Cho
#
# reads mge files and converts to ppm

from __future__ import print_function

import argparse
import sys

from util import getbit, pack


def convert(input_image_stream, output_image_stream):
    def dump(x):
        c = palette[x]
        out.write(pack([(getbit(c, 5) * 2 + getbit(c, 2)) * 85,
                        (getbit(c, 4) * 2 + getbit(c, 1)) * 85,
                        (getbit(c, 3) * 2 + getbit(c, 0)) * 85]))

    f = input_image_stream
    out = output_image_stream
    palette = [ord(ii) for ii in f.read(16)]
    out.write('P6\n320 192\n255\n')
    for jj in range(192):
        for ii in range(160):
            c = ord(f.read(1))
            dump(c >> 4)
            dump(c & 7)


VERSION = '2018.09.08'
DESCRIPTION = """Convert RS-DOS HRS images to PPM
Copyright (c) 2018 by Mathieu Bouchard
Copyright (C) 2018 by Jamie Cho
Version: {}""".format(VERSION)


def main():
    start(sys.argv[1:])


def start(argv):
    parser = argparse.ArgumentParser(description=DESCRIPTION,
      formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_image',
      metavar='image.hrs',
      type=argparse.FileType('rb'),
      nargs='?',
      default=sys.stdin,
      help='input HRS image file')
    parser.add_argument('output_image',
      metavar='image.ppm',
      type=argparse.FileType('wb'),
      nargs='?',
      default=sys.stdout,
      help='output PPM image file')
    parser.add_argument('--version',
      action='version',
      version='%(prog)s {}'.format(VERSION))
    args = parser.parse_args(argv)

    convert(args.input_image, args.output_image)
    args.output_image.close()
    args.input_image.close()


if __name__ == '__main__':
    main()

