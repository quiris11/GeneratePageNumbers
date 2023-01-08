GeneratePageNumbers [![Release](https://img.shields.io/github/release/quiris11/generatepagenumbers.svg)](https://github.com/quiris11/generatepagenumbers/releases/latest)
==================

Tool for generating page numbers for Kindle e-ink devices.

```
usage: GeneratePageNumbers [-h] [-V] [-s] [-o] [-d [DAYS]] [-l] [--mark-real-pages] kindle_directory

positional arguments:
  kindle_directory      directory where is a Kindle Paperwhite mounted

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -s, --silent          print less informations
  -o, --overwrite-apnx  overwrite APNX files
  -d [DAYS], --days [DAYS]
                        only "younger" ebooks than specified DAYS will be processed (default: 7 days).
  -l, --lubimy-czytac   [DISABLED] download real pages from lubimyczytac.pl (time-consuming process!) (only with -d)
  --mark-real-pages     mark computed pages as real pages (only with -l and -d)
```

#### Additional requirements:
* python -m pip install pyinstaller (for compilation only)

#### Compilation tips for creating standalone applications with Pyinstaller tool:
* build on Mac (with Python 3.9.x from Homebrew):
```
pyinstaller -Fn GeneratePageNumbers ~/github/GeneratePageNumbers/__main__.py
```
* build on Windows (with Python 3.9.x):
```
C:\Python27\Scripts\pyinstaller.exe -Fn GeneratePageNumbers .\GeneratePageNumbers\__main__.py
```
