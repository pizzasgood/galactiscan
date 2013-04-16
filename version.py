#!/usr/bin/python2
# vim: ts=4 : sts=4 : sw=4 : et :
import os.path

name = "galactiscan"
fancy_name = "Galactiscan"
number = "0.9"
string = "%s %s" % (name, number)
fancy_string = "%s %s" % (fancy_name, number)
description = "A tool for maintaining and querying a database of survey scans from Shores of Hazeron."

url = "https://github.com/pizzasgood/galactiscan"
copyright = "Copyright (C) 2013  Pizzasgood"

license_name = "GPL"
license_version = "3"
license_fancy_name = "GNU General Public License"
license_string = "%s Version %s" % (license_fancy_name, license_version)
license_url = "http://www.gnu.org/licenses/gpl.html"
license_filename = "LICENSE"

def getLicensePath():
    """Return the path to the license file."""
    program_directory = os.path.dirname(__file__)
    return "%s/%s" % (program_directory, license_filename)

def getLicenseBody():
    """Return the text of the license file."""
    path = getLicensePath()
    if os.path.isfile(path):
        #read the license file
        f = open(getLicensePath())
        text = f.read()
        f.close()
    else:
        #unable to find license file, so make do with what we have
        text = license_string
    return text

