#!/usr/bin/python2
# vim: ts=4 : sts=4 : sw=4 : et :

import sqlite3
import datetime
import os.path
import sys

import survey
import data
import gui

def usage(ret = 0):
    print """galactiscan [-h|--help] <options> [file1 [file2..]]
If neither options nor file parameters are given, open the gui.
Otherwise, if no options are given, load the files into the database

Options:
    --help                  shows this message
    --clear-db              deletes the database
    --tl <tl> [name]        shows resources >= tl, optionally matching name
    --name <name> [tl]      shows resources matching name, optionally >= tl
    --planet <name> [tl]    shows resources on planet named 'name', optionally >= tl
    --system <name> [tl]    shows resources on system named 'name', optionally >= tl
"""
    exit(ret)

def add_files(files):
    data.create_tables()
    for f in files:
        surveys = survey.process_survey_file(f)
        for s in surveys:
            data.save_survey(s)

files = []

if len(sys.argv) > 1:
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-h' or sys.argv[i] == '--help':
            usage()
        elif sys.argv[i] == '--clear-db':
            if len(sys.argv) == 2:
                data.drop_tables()
            else:
                print "Error: The --clear-db option must not be used with other options, else operator error is assumed."
                exit(1)
        elif sys.argv[i] == '--tl' and len(sys.argv) > i+1:
            if len(sys.argv) > i+2:
                rows = data.find_resources(name=sys.argv[i+2], mintl=sys.argv[i+1])
                i+=2
            else:
                rows = data.find_resources(name=sys.argv[i+1])
                i+=1
            data.display_rows(rows)
            exit(0)
        elif sys.argv[i] == '--name' and len(sys.argv) > i+1:
            if len(sys.argv) > i+2:
                rows = data.find_resources(name=sys.argv[i+1], mintl=sys.argv[i+2])
                i+=2
            else:
                rows = data.find_resources(name=sys.argv[i+1])
                i+=1
            data.display_rows(rows)
            exit(0)
        elif sys.argv[i] == '--planet' and len(sys.argv) > i+1:
            if len(sys.argv) > i+2:
                rows = data.find_resources(planet=sys.argv[i+1], mintl=sys.argv[i+2])
                i+=2
            else:
                rows = data.find_resources(planet=sys.argv[i+1])
                i+=1
            data.display_rows(rows)
            exit(0)
        elif sys.argv[i] == '--system' and len(sys.argv) > i+1:
            if len(sys.argv) > i+2:
                rows = data.find_resources(system=sys.argv[i+1], mintl=sys.argv[i+2])
                i+=2
            else:
                rows = data.find_resources(system=sys.argv[i+1])
                i+=1
            data.display_rows(rows)
            exit(0)
        elif os.path.isfile(sys.argv[i]):
            files.append(sys.argv[i])
        else:
            print "unknown argument: %s" % sys.argv[i]
            usage(1)
        i+=1

    #add any files that were specified
    if len(files) > 0:
        add_files(files)

else:
    gui.main()













