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


def get_real_pages(csvfile, mark_real_pages):

    import os
    import csv
    import urllib
    import urllib2
    import unicodedata
    import sys

    try:
        from lxml.html import fromstring
    except ImportError as e:
        sys.exit('CRITICAL! ' + e)

    def strip_accents(text):
        return ''.join(c for c in unicodedata.normalize(
            'NFKD', text
        ) if unicodedata.category(c) != 'Mn')

    def get_html_page(url):
        req = urllib2.Request(url)
        return fromstring(urllib2.urlopen(req).read())

    def search_book(category):
        url = 'http://lubimyczytac.pl/szukaj/ksiazki'
        data = urllib.urlencode({
            'phrase': category,
            'main_search': '1',
        })
        url = url + '?' + data
        return get_html_page(url)

    def get_pages_book_type(url):
        tree = get_html_page(url)
        pages = tree.xpath(
            '//div[@class="profil-desc-inline"]'
            '//dt[contains(text(),"liczba stron")]'
            '/following-sibling::dd/text()'
        )
        book_types = tree.xpath('//div[contains(@class, "cover-book-type")]')
        if book_types:
            book_type = book_types[0].text
        else:
            book_type = ''
        if pages:
            return pages[0], book_type
        else:
            return None, book_type

    def get_search_results(tree, author, title):
        title = title.decode('UTF-8').lower().encode('UTF-8')
        author = author.decode('UTF-8').lower().encode('UTF-8')
        results = tree.xpath('*//div[contains(@class,"book-data")]')
        if len(results) == 1:
            book_url = results[0].xpath(
                './div[contains(@class,"book-general-data")]'
                '/a[@class="bookTitle"]/@href'
            )[0]
            return book_url
        elif len(results) == 0:
            print('  No results...')
        else:
            for result in results:
                try:
                    title_f = result.xpath(
                        './div[contains(@class,"book-general-data")]'
                        '//a[@class="bookTitle"]//text()'
                    )[0]
                except IndexError:
                    title_f = ''
                authors_f = result.xpath(
                    './div[contains(@class,"book-general-data")]'
                    '//a[contains(@href,"autor")]//text()'
                )
                author_f = ''
                for a in authors_f:
                    author_f = author_f + ', ' + a
                author_f = author_f.lstrip(', ')
                author = author.replace('; ', ', ').replace(' i ', ', ')
                book_url = result.xpath(
                    './div[contains(@class,"book-general-data")]'
                    '/a[@class="bookTitle"]/@href'
                )[0]
                if len(title) > len(title_f):
                    sub_title = len(title_f)
                else:
                    sub_title = len(title)
                author_f = author_f.lower().encode('UTF-8')
                title_f = title_f.lower().encode('UTF-8')
                if title[:sub_title] == title_f[:sub_title]:
                    a_fs = strip_accents(
                        author_f.decode('UTF-8')
                    ).replace(u"\xf8", 'o')
                    a_s = strip_accents(
                        author.decode('UTF-8')
                    ).replace(u"\xf8", 'o')
                    a_fsrt = ''.join(sorted(set(a_fs))).strip()
                    a_srt = ''.join(sorted(
                        set(a_s))).strip().replace(',', '')
                    if author == author_f:
                        return book_url
                        break
                    elif a_s == a_fs:
                        return book_url
                        break
                    elif a_srt == a_fsrt:
                        return book_url
                        break
            print('  No matches in results...')

    if os.path.isfile(os.path.join(csvfile)):
        with open(os.path.join(
                csvfile), 'r', newline='', encoding='utf-8') as f:
            csvread = csv.reader(
                f, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_ALL
            )
            dumped_list = list(csvread)
            for row in dumped_list:
                try:
                    if row[0] == 'asin' or row[5] == 'True' or not (
                            row[1].lower() == 'pl' or 
                            row[1].lower() == 'pl-pl'):
                        continue
                    print('* Searching for: ' + row[2].decode(
                          'UTF-8') + ' - ' + row[3].decode('UTF-8'))
                except IndexError:
                    continue
                try:
                    root = search_book(row[3])
                    if len(root.xpath(
                        '*//div[contains(@class,"book-data")]'
                    )) == 0:
                        root = search_book(row[3].split('.')[0])
                    book_url = get_search_results(root, row[2], row[3])
                except urllib2.HTTPError:
                    print('  ! HTTP error. Unable to find the book details...')
                    book_url = None
                if book_url:
                    pages, book_type = get_pages_book_type(book_url)
                    if pages is not None:
                        row[4] = pages
                        row[5] = True
                        print('  Book pages:', pages)
                    elif book_type == 'E-book':
                        print('  ! E-book format only! '
                              'Using computed pages as real pages...')
                        row[5] = True
                    else:
                        print('  ! There are no page number set '
                              'on the site: ' + book_url)
                elif mark_real_pages:
                    print('  ! Marking computed pages as real pages...')
                    row[5] = True

                with open(os.path.join(
                        csvfile), 'w', newline='', encoding='utf-8') as f:
                    csvwrite = csv.writer(
                        f, delimiter=';', quotechar='"',
                        quoting=csv.QUOTE_ALL
                    )
                    csvwrite.writerows(dumped_list)
