Galactiscan
===========

A tool for maintaining and querying a database of survey scans from [Shores of Hazeron](http://www.hazeron.com/).

**Warning**:  This software is still in Alpha.  It is still very much under development and may have bugs, inadequate documentation, missing features, offensive typos, sudden radical changes between versions, and who knows what else.  Also, it is currently only being developed and tested in Linux.  It *should* work in any OS that supports Python, Sqlite3, and wxWidgets, however.



Dependencies
------------

[Python 2.x](http://www.python.org/)

[pysqlite](https://pypi.python.org/pypi/pysqlite) (this might be bundled with Python, not sure)

[wxPython](http://www.wxpython.org/)

[wxWidgets](http://www.wxwidgets.org/)



Installation
------------

You don't install Galactiscan, currently.  Just check out the repository, stick it wherever, and run galactiscan.py out of the current directory.  Please do not simply click on it, as it currently saves data to whatever the current directory is.  If you simply click it, the current directory might be / or C:\ or someplace equally silly.  Yes, I'll fix that soon, but for now either make a wrapper script to launch it, or launch it from the terminal.

Someday it will have an optional installer, but that is low priority right now.



Adding Data
-----------

You can add data in a few ways.  The simplest is to copy the survey report right out of the game, and then click the "Paste" toolbar button on Galactiscan.  You can also use the "Open" button to load data directly out of a text file.  Note that you can open multiple files in one go, by holding the Ctrl key while selecting them.  Galactiscan will also happily load files that contain multiple concatinated reports.  Finally, you can add files from the commandline, like so:

`./galactiscan.py /path/to/some/file.txt /path/to/other/file.txt`

The data will be saved in an sqlite3 database in the current directory, named database.sqlite3, and automatically loaded from then on.  Only the single database is supported for now, so if you want multiple databases you'll have to do it by manually juggling the files or launching Galactiscan from different directories.

You can delete everything in the database by using the "Clear" button.  There is no undo yet, so please be careful.

There is currently no way to delete specific subsets of data.  If you really want to do that, you can edit the database file manually using any tool that supports sqlite3.  You can look through the data.py file to understand the schema.



Using
-----

Once you have data stored, you can fill out any relevant fields in the search area at the bottom, and then either press Enter or click the "Search" button.  The results will appear in a list, which you can sort following various criteria by clicking on the headers.

You can use the "radius" and "center" fields to restrict the search to locations roughly within "radius" sectors of the center point.  Note that it currently cheats and searches a cube rather than a sphere, with side lengths of twice the radius.  This will eventually change.

Note also that all coordinate values in the search fieldw should be in sectors, not parsecs.  This is likely to change eventually, at least for the center/radius fields.


Known Issues
------------

Trying to search with an empty database will cause an error.

Trying to load text that isn't a survey report will cause an error.

Doing a query that pulls up thousands of results can be slow.

It may be possible to give sectors, systems, or worlds malicious names that will make them be processed incorrectly, potentially even ovewriting valid data.  So, backup your database from time to time.  (You should do that anyway.)
