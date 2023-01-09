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

import sys
import os
import csv
import shutil
import tempfile

from datetime import datetime

from lib.apnx import APNXBuilder
from lib.pages import find_exth
from lib.pages import get_pages
from lib.get_real_pages import get_real_pages
from lib.pages import mobi_header_fields   


def clean_temp(sourcedir):
    for p in os.listdir(os.path.join(sourcedir, os.pardir)):
        if 'epubQTools-tmp-' in p:
            if os.path.isdir(os.path.join(sourcedir, os.pardir, p)):
                try:
                    shutil.rmtree(os.path.join(sourcedir, os.pardir, p))
                except Exception:
                    if sys.platform == 'win32':
                        os.system('rmdir /S /Q \"{}\"'.format(
                            os.path.join(sourcedir, os.pardir, p)
                        ))
                    else:
                        raise


def asin_list_from_csv(mf):
    if os.path.isfile(mf):
        with open(mf, 'r', newline='', encoding='utf-8') as f:
            csvread = csv.reader(f, delimiter=';', quotechar='"',
                                 quoting=csv.QUOTE_ALL)
            asinlist = []
            filelist = []
            for row in csvread:
                try:
                    if row[0] != '* NONE *':
                        asinlist.append(row[0])
                except IndexError:
                    continue
                filelist.append(row[6])
            return asinlist, filelist
    else:
        with open(mf, 'w', newline='', encoding='utf-8') as o:
            csvwrite = csv.writer(o, delimiter=';', quotechar='"',
                                  quoting=csv.QUOTE_ALL)
            csvwrite.writerow(
                ['asin', 'lang', 'author', 'title', 'pages', 'is_real',
                 'file_path']
            )
            return [], []


def dump_pages(asinlist, filelist, gpnCSVFile, dirPath, mobiFile, is_verbose):
    row = get_pages(dirPath, mobiFile, is_verbose)
    if row is None:
        return
    if row[0] in asinlist:
        return
    if row[6] in filelist:
        return
    with open(gpnCSVFile, 'a', newline='', encoding='utf-8') as o:
        print('* Updating book pages CSV file...')
        print(row)
        csvwrite = csv.writer(o, delimiter=';', quotechar='"',
                              quoting=csv.QUOTE_ALL)
        csvwrite.writerow(row)


def generate_apnx_files(docs, is_verbose, is_overwrite_apnx, days,
                        tempdir):
    apnx_builder = APNXBuilder()
    if days is not None:
        dtt = datetime.today()
        days_int = int(days)
    else:
        days_int = 0
        diff = 0
    for root, dirs, files in os.walk(docs):
        for name in files:
            if 'documents' + os.path.sep + 'dictionaries' in root:
                if is_verbose:
                    print('! Excluded dictionary:', name)
                continue
            mobi_path = os.path.join(root, name)
            if "attachables" in mobi_path:
                continue
            if days is not None:
                try:
                    dt = os.path.getmtime(mobi_path)
                except OSError:
                    # raise
                    continue
                dt = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
                dt = datetime.strptime(dt, '%Y-%m-%d')
                diff = (dtt - dt).days
            if name.lower().endswith((
                    '.azw3', '.mobi', '.azw')) and diff <= days_int:
                sdr_dir = os.path.join(root, os.path.splitext(
                                       name)[0] + '.sdr')
                if not os.path.isdir(sdr_dir):
                    os.makedirs(sdr_dir)
                apnx_path = os.path.join(sdr_dir, os.path.splitext(
                                         name)[0] + '.apnx')
                # print(apnx_path)
                if not os.path.isfile(apnx_path) or is_overwrite_apnx:
                    if '!DeviceUpgradeLetter!' in name:
                        continue
                    if is_verbose:
                        print('* Generating APNX file for "%s"' % name)
                    if os.path.isfile(os.path.join(
                            tempdir, '!gpn_pages.csv')):
                        with open(os.path.join(
                                tempdir, '!gpn_pages.csv'
                        ), 'r', newline='', encoding='utf-8') as f1:
                            csvread = csv.reader(
                                f1, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_ALL
                            )
                            with open(mobi_path, 'rb') as f2:
                                mobi_content = f2.read()
                            id, ver, title, locations, di, do = mobi_header_fields(mobi_content)  # noqa
                            if (di != 0 or do != 0):
                                if is_verbose:
                                    print(name + ': dictionary file. '
                                          'Skipping…')
                                continue
                            if mobi_content[60:68] != b'BOOKMOBI':
                                if is_verbose:
                                    print('* Invalid file format. Skipping...')
                                asin = ''
                            else:
                                try:
                                    asin = find_exth(
                                        113, mobi_content).decode('utf-8')
                                except AttributeError:
                                    asin = '* NONE *' 
                            found = False
                            for i in csvread:
                                # print(asin, name)
                                try:
                                    if (
                                        i[0] == asin and i[0] != '* NONE *'
                                    ) or (
                                        i[0] == '* NONE *' and i[6] == name
                                    ):
                                        if is_verbose:
                                            print(
                                                '  * Using %s pages defined '
                                                'in CSV file in Kindle '
                                                'folder' % (i[4]))
                                        apnx_builder.write_apnx(
                                            mobi_path, apnx_path, int(i[4])
                                        )
                                        found = True
                                        continue
                                except IndexError:
                                    continue
                            if not found:
                                if is_verbose:
                                    print(
                                        '  ! Book not found in gpn_pages.csv.'
                                        ' Fast algorithm used...')
                                apnx_builder.write_apnx(mobi_path, apnx_path)
                    else:
                        apnx_builder.write_apnx(mobi_path, apnx_path)


def generate_page_numbers(is_silent, is_overwrite_apnx, kindlepath, days,
                          lubimy_czytac, mark_real_pages):
    docs = os.path.join(kindlepath, 'documents')
    is_verbose = not is_silent
    if days is not None:
        print('Notice! Processing files not older than ' + days + ' days.')

    # move CSV file to computer temp dir to speed up updating process
    tempdir = tempfile.mkdtemp(suffix='', prefix='gpn-tmp-')
    csv_pages_name = '!gpn_pages.csv'
    csv_pages = os.path.join(tempdir, csv_pages_name)
    if os.path.isfile(os.path.join(docs, csv_pages_name)):
        shutil.copy2(os.path.join(docs, csv_pages_name),
                     os.path.join(tempdir, csv_pages_name))

    # load ASIN list from CSV
    asinlist, filelist = asin_list_from_csv(csv_pages)

    if lubimy_czytac and days:
        print("START of downloading real book page numbers...")
        get_real_pages(os.path.join(
            tempdir, '!gpn_pages.csv'), mark_real_pages)
        print("FINISH of downloading real book page numbers...")

    print("START of updating CSV file…")
    if days is not None:
        dtt = datetime.today()
        days_int = int(days)
    else:
        days_int = 0
        diff = 0
    for root, dirs, files in os.walk(docs):
        for name in files:
            mobi_path = os.path.join(root, name)
            if days is not None:
                try:
                    dt = os.path.getmtime(mobi_path)
                except OSError:
                    # raise
                    continue
                dt = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
                dt = datetime.strptime(dt, '%Y-%m-%d')
                diff = (dtt - dt).days
            if name.lower().endswith(
                    ('.azw3', '.mobi', '.azw')) and diff <= days_int:
                dump_pages(asinlist, filelist, csv_pages, root, name, 
                           is_verbose)
    print("FINISH  of updating CSV file…")

    print("START of generating book page numbers (APNX files)...")
    generate_apnx_files(docs, is_verbose, is_overwrite_apnx, days, tempdir)
    print("FINISH of generating book page numbers (APNX files)...")
    
    shutil.copy2(os.path.join(tempdir, csv_pages_name),
                 os.path.join(docs, csv_pages_name))
    clean_temp(tempdir)
    return 0
