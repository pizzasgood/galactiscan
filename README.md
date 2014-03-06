Galactiscan
===========

An unofficial tool for maintaining and querying a database of survey scans from [Shores of Hazeron](http://www.hazeron.com/).



License
-------

This program is distributed under the GNU General Public License.  See the file LICENSE for more details.



Dependencies
------------

[Python 2.x](http://www.python.org/)

[wxPython](http://www.wxpython.org/)



Installation
------------

You don't install Galactiscan, currently.  Just check out the repository, stick it wherever, and run galactiscan.py using python2.  You'll need to go to "File -> Define DB" the first time you run it, and select a location to save the database file (which is a generic sqlite3 database, fyi).  Your choice will be remembered and used automatically from then on.  Otherwise it will just use 'database.sqlite3' in the local directory, which may not be what you want.

You may need to also go to "File -> Define Mail Cache" to tell it where your Hazeron mail cache is (or if you want to point it somewhere else, so that you can manually manage which survey reports it reads).  It will default to "~/Shores of Hazeron/Mail".

Someday there will be an optional installer, but that is low priority right now.



Adding Data
-----------

You add data to Galactiscan by ensuring it has the correct location for your mail cache, and then clicking the "Refresh" button on the toolbar.  It will peruse that directory and process any Survey Scan reports that it has not already processed.  You can also use the "Add" button to load specific mail files (e.g. that an ally has sent you outside of the game).  Passing it filenames on the commandline also works:

`./galactiscan.py /path/to/some/file.m /path/to/some/otherfile.m`

The data will be saved in an sqlite3 database at whatever location you defined for the database, and automatically loaded from then on.  If you want to switch databases on the fly, just go to "File -> Define DB" and select a new one.  The old database will be unloaded and the new one loaded.  If you define a file that doesn't exist, an empty one will be created.

You can delete everything in the database by using the "File -> Clear" option.  There is no undo yet, so please be careful.

There is currently no way to delete specific subsets of data.  If you really want to do that, you can edit the database file manually using any tool that supports sqlite3.  You can look through the data.py file to understand the schema.



Using
-----

Once you have data stored, you can fill out any relevant fields in the search area at the bottom, and then either press Enter or click the "Search" button.  The results will appear in a list, which you can sort following various criteria by clicking on the headers.

You can use the "radius" and "center" fields to restrict the search to locations roughly within "radius" sectors of the center point.  Note that it currently cheats and searches a cube rather than a sphere, with side lengths of twice the radius.  This will eventually change.

Note also that all coordinate values in the search fields should be in sectors, not parsecs.  This is likely to change eventually, at least for the center/radius fields.


Known Issues
------------

Trying to load text that isn't a survey report can cause an error.

Doing a query that pulls up thousands of results can be slow.

It may be possible to give sectors, systems, or worlds malicious names that will make them be processed incorrectly, potentially even ovewriting valid data.  So, backup your database from time to time.  (You should do that anyway.)

Multiple galaxies are not yet supported; surveys offer no means to identify the galaxy they came from.
