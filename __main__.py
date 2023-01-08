#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of GeneratePageNumbers, licensed under
# GNU Affero GPLv3 or later.
# Copyright © Robert Błaut. See NOTICE for more information.
#
# This script extracts missing Cover Thumbnails from eBooks downloaded
# from Amazon Personal Documents Service and side loads them
# to your Kindle Paperwhite.
#

import argparse
import os
import sys
from lib.generate_page_numbers import generate_page_numbers
from distutils.util import strtobool

__license__ = 'GNU Affero GPL v3'
__copyright__ = '2023, Robert Błaut listy@blaut.biz'
__appname__ = u'GeneratePageNumbers'
numeric_version = (1, 0, 0)
__version__ = '.'.join(map(str, numeric_version))
__author__ = u'Robert Błaut <listy@blaut.biz>'


parser = argparse.ArgumentParser()
parser.add_argument('-V', '--version', action='version',
                    version="%(prog)s (version " + __version__ + ")")
parser.add_argument("kindle_directory", help="directory where is a Kindle"
                    " Paperwhite mounted")
parser.add_argument("-s", "--silent", help="print less informations",
                    action="store_true")
parser.add_argument("-o", "--overwrite-apnx", help="overwrite APNX files",
                    action="store_true")
parser.add_argument('-d', '--days', nargs='?', metavar='DAYS', const='7',
                    help='only "younger" ebooks than specified DAYS will '
                    'be processed (default: 7 days).')
parser.add_argument("-l", "--lubimy-czytac",
                    help="[DISABLED] download real pages from lubimyczytac.pl "
                    "(time-consuming process!) (only with -d)",
                    action="store_true")
parser.add_argument("--mark-real-pages",
                    help="mark computed pages as real pages "
                    "(only with -l and -d)",
                    action="store_true")

if sys.platform == 'darwin':
    parser.add_argument("-e", "--eject",
                        help="eject Kindle after completing process",
                        action="store_true")


args = parser.parse_args()

kindlepath = args.kindle_directory
docs = os.path.join(kindlepath, 'documents')


def user_yes_no_query(question):
    sys.stdout.write('%s [y/n]\n' % question)
    while True:
        try:
            return strtobool(input().lower())
        except ValueError:
            sys.stdout.write('Please respond with \'y\' or \'n\'.\n')


if __name__ == '__main__':
    # args.lubimy_czytac set up to False 
    generate_page_numbers(args.silent, args.overwrite_apnx, kindlepath,
                          args.days, False,
                          args.mark_real_pages)
    if sys.platform == 'darwin':
        if args.eject:
            os.system('diskutil eject ' + kindlepath)
