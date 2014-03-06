#!/usr/bin/python2
# vim: ts=4 : sts=4 : sw=4 : et :

import sqlite3
import datetime
import os.path
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ColumnSorterMixin

import version
import survey
import data
import about


orbit_zones = [
    'Inferno Zone',
    'Inner Zone',
    'Habitable Zone',
    'Outer Zone',
    'Frigid Zone',
    ]

body_kinds = [
    'Ringworld',
    'Planet',
    'Large Moon',
    'Moon',
    'Ring',
    'Gas Giant',
    'star',
    ]


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class SortedListCtrl(AutoWidthListCtrl, ColumnSorterMixin):
    def __init__(self, parent, data):
        AutoWidthListCtrl.__init__(self, parent)
        ColumnSorterMixin.__init__(self, len(data.values()[0]))
        self.itemDataMap = data

    def GetListCtrl(self):
        return self




class ResultListCtrl(SortedListCtrl):
    def __init__(self, parent, data):
        SortedListCtrl.__init__(self, parent, data)

        #build the columns
        self.InsertColumn(0, 'name', width=140)
        self.InsertColumn(1, 'tl', wx.LIST_FORMAT_RIGHT, 50)
        self.InsertColumn(2, 'quality', wx.LIST_FORMAT_RIGHT, 60)
        self.InsertColumn(3, 'prev', wx.LIST_FORMAT_RIGHT, 60)
        self.InsertColumn(4, 'diameter', width=80)
        self.InsertColumn(5, 'kind', width=80)
        self.InsertColumn(6, 'type', width=80)
        self.InsertColumn(7, 'zone', width=50)
        self.InsertColumn(8, 'world', width=140)
        self.InsertColumn(9, 'system', width=140)
        self.InsertColumn(10, 'sector', width=140)
        self.InsertColumn(11, 'coords', width=80)

        #insert the data
        self.InsertData(data)

    def InsertData(self, data):
        items = data.items()
        for key, i in items:
            index = self.InsertStringItem(sys.maxint, i[0])
            for k in range(1, len(i)):
                self.SetStringItem(index, k, i[k])
            self.SetItemData(index, key)

    def SetData(self, data):
        self.DeleteAllItems()
        self.InsertData(data)
        self.itemDataMap = data



class Menubar(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)

        fileMenu = wx.Menu()
        helpMenu = wx.Menu()

        fitem = fileMenu.Append(wx.ID_OPEN, 'Define DB', 'Define Database')
        parent.Bind(wx.EVT_MENU, parent.DefineDatabase, fitem)

        fitem = fileMenu.Append(wx.ID_PREFERENCES, 'Define Mail Cache', 'Define Mail Cache')
        parent.Bind(wx.EVT_MENU, parent.DefineMailcache, fitem)

        fitem = fileMenu.Append(wx.ID_CLEAR, 'Clear DB', 'Clear database')
        parent.Bind(wx.EVT_MENU, parent.ClearDatabase, fitem)

        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        parent.Bind(wx.EVT_MENU, parent.OnQuit, fitem)

        hitem = helpMenu.Append(wx.ID_ABOUT, 'About', 'About application')
        parent.Bind(wx.EVT_MENU, parent.ShowAbout, hitem)

        self.Append(fileMenu, '&File')
        self.Append(helpMenu, '&Help')
        parent.SetMenuBar(self)



class Toolbar(wx.BoxSizer):
    def __init__(self, parent, grandparent):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        #create the buttons
        self.update_button = wx.Button(parent, id=wx.ID_REFRESH, style=wx.BU_EXACTFIT)
        self.add_button = wx.Button(parent, id=wx.ID_ADD, style=wx.BU_EXACTFIT)

        #add the buttons to the widget
        self.Add(self.update_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT)
        self.Add(self.add_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT)

        #bind the buttons to actions
        grandparent.Bind(wx.EVT_BUTTON, grandparent.Update,  id=self.update_button.GetId())
        grandparent.Bind(wx.EVT_BUTTON, grandparent.AddFile,  id=self.add_button.GetId())



class SearchControls(wx.BoxSizer):
    def __init__(self, parent, grandparent):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        resources = [
            'Air',
            'Animal Carcass',
            'Antiflux Particles',
            'Beans',
            'Bolite',
            'Borexino Precipitate',
            'Cheese',
            'Coal',
            'Cryozine',
            'Crystals',
            'Eggs',
            'Eludium',
            'Fertilizer',
            'Fish',
            'Fruit',
            'Gems',
            'Grain',
            'Grapes',
            'Herbs',
            'Hops',
            'Hydrogen',
            'Ice',
            'Ioplasma',
            'Log',
            'Lumenite',
            'Magmex',
            'Milk',
            'Minerals',
            'Myrathane',
            'Natural Gas',
            'Nuts',
            'Oil',
            'Ore',
            'Phlogiston',
            'Plant Fiber',
            'Polytaride',
            'Radioactives',
            'Spices',
            'Stone',
            'Sunlight',
            'Type A Preons',
            'Type B Preons',
            'Type F Preons',
            'Type G Preons',
            'Type K Preons',
            'Type M Preons',
            'Type O Preons',
            'Vegetable',
            'Vegetation Density',
            'Vulcanite',
            'Water in the Environment',
            ]

        name_l = wx.StaticText(parent, label="Name:")
        self.name_field = wx.ComboBox(parent, style=wx.TE_PROCESS_ENTER, choices=resources)
        tl_l = wx.StaticText(parent, label="Min TL:")
        self.tl_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.orbit_field = wx.ListBox(parent, style=wx.LB_EXTENDED, choices=orbit_zones)
        self.body_field = wx.ListBox(parent, style=wx.LB_EXTENDED, choices=body_kinds)
        planet_l = wx.StaticText(parent, label="Planet:")
        self.planet_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        system_l = wx.StaticText(parent, label="System:")
        self.system_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        sector_l = wx.StaticText(parent, label="Sector:")
        self.sector_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        minsec_l = wx.StaticText(parent, label="Min Sec:")
        self.minsecx_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.minsecy_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.minsecz_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        maxsec_l = wx.StaticText(parent, label="Max Sec:")
        self.maxsecx_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.maxsecy_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.maxsecz_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        center_l = wx.StaticText(parent, label="Center Coords:")
        self.centerx_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.centery_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        self.centerz_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        radius_l = wx.StaticText(parent, label="Search Radius:")
        self.radius_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)

        self.reset_button = wx.Button(parent, id=wx.ID_CLEAR)
        self.search_button = wx.Button(parent, id=wx.ID_FIND)

        hbox_inputs = wx.BoxSizer(wx.HORIZONTAL)
        vbox_l = wx.BoxSizer(wx.VERTICAL)
        vbox_r = wx.BoxSizer(wx.VERTICAL)
        hbox_bodies = wx.BoxSizer(wx.HORIZONTAL)
        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_coords_ls = wx.BoxSizer(wx.VERTICAL)
        vbox_coords = wx.BoxSizer(wx.VERTICAL)
        vbox_radius = wx.BoxSizer(wx.VERTICAL)
        hbox_minsec = wx.BoxSizer(wx.HORIZONTAL)
        hbox_maxsec = wx.BoxSizer(wx.HORIZONTAL)
        hbox_center = wx.BoxSizer(wx.HORIZONTAL)
        hbox_radius = wx.BoxSizer(wx.HORIZONTAL)

        self.Add(hbox_inputs, proportion=1, flag=wx.EXPAND)
        hbox_inputs.Add(vbox_l, proportion=1, flag=wx.EXPAND)
        hbox_inputs.Add(vbox_r, proportion=3, flag=wx.EXPAND)

        vbox_l.Add(hbox1, proportion=0, flag=wx.EXPAND)
        vbox_l.Add(hbox2, proportion=0, flag=wx.EXPAND)
        vbox_l.Add(hbox3, proportion=0, flag=wx.EXPAND)
        vbox_l.Add(hbox4, proportion=1, flag=wx.EXPAND)
        vbox_r.Add(hbox_bodies, proportion=1, flag=wx.EXPAND)

        hbox3.Add(vbox_coords_ls, proportion=0, flag=wx.LEFT, border=5)
        hbox3.Add(vbox_coords,    proportion=1)
        hbox3.Add(vbox_radius,    proportion=2)

        hbox4.Add(hbox_buttons, proportion=0, flag=wx.EXPAND)

        vbox_coords.Add(hbox_minsec, proportion=0, flag=wx.EXPAND)
        vbox_coords.Add(hbox_maxsec, proportion=0, flag=wx.EXPAND)
        vbox_radius.Add(hbox_center, proportion=0, flag=wx.EXPAND)
        vbox_radius.Add(hbox_radius, proportion=0, flag=wx.EXPAND)

        hbox1.Add(name_l,            proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.name_field,   proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(tl_l,              proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.tl_field,     proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox2.Add(planet_l,          proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.planet_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(system_l,          proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.system_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(sector_l,          proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.sector_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        vbox_coords_ls.Add(minsec_l, proportion=1, flag=wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM, border=5)
        vbox_coords_ls.Add(maxsec_l, proportion=1, flag=wx.ALIGN_LEFT|wx.TOP|wx.BOTTOM, border=5)

        hbox_minsec.Add(self.minsecx_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_minsec.Add(self.minsecy_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_minsec.Add(self.minsecz_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox_maxsec.Add(self.maxsecx_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_maxsec.Add(self.maxsecy_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_maxsec.Add(self.maxsecz_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox_center.Add(center_l,           proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_center.Add(self.centerx_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_center.Add(self.centery_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_center.Add(self.centerz_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox_radius.Add(radius_l,           proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_radius.Add(self.radius_field,  proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox_buttons.Add(self.reset_button,  proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_buttons.Add(self.search_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox_bodies.Add(self.orbit_field,  proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.EXPAND, border=5)
        hbox_bodies.Add(self.body_field,  proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT|wx.EXPAND, border=5)

        #bind the search controls
        grandparent.Bind(wx.EVT_BUTTON, self.OnReset,  id=self.reset_button.GetId())
        grandparent.Bind(wx.EVT_BUTTON, grandparent.OnSearch, id=self.search_button.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.name_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.tl_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.planet_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.system_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.sector_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.minsecx_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.minsecy_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.minsecz_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.maxsecx_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.maxsecy_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.maxsecz_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.centerx_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.centery_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.centerz_field.GetId())
        grandparent.Bind(wx.EVT_TEXT_ENTER, grandparent.OnSearch, id=self.radius_field.GetId())

    def OnReset(self, e):
        self.name_field.SetValue("")
        self.tl_field.SetValue("")
        self.orbit_field.SetSelection(wx.NOT_FOUND)
        self.body_field.SetSelection(wx.NOT_FOUND)
        self.planet_field.SetValue("")
        self.system_field.SetValue("")
        self.sector_field.SetValue("")
        self.minsecx_field.SetValue("")
        self.minsecy_field.SetValue("")
        self.minsecz_field.SetValue("")
        self.maxsecx_field.SetValue("")
        self.maxsecy_field.SetValue("")
        self.maxsecz_field.SetValue("")
        self.centerx_field.SetValue("")
        self.centery_field.SetValue("")
        self.centerz_field.SetValue("")
        self.radius_field.SetValue("")



class Galactiscan(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Galactiscan, self).__init__(*args, **kwargs)

        self.InitUI()

    def OnSearch(self, e):
        self.status.SetStatusText("Searching...")

        name = self.search_controls.name_field.GetValue()
        tl = self.search_controls.tl_field.GetValue()
        planet = self.search_controls.planet_field.GetValue()
        system = self.search_controls.system_field.GetValue()
        sector = self.search_controls.sector_field.GetValue()
        minsecx = self.search_controls.minsecx_field.GetValue()
        minsecy = self.search_controls.minsecy_field.GetValue()
        minsecz = self.search_controls.minsecz_field.GetValue()
        maxsecx = self.search_controls.maxsecx_field.GetValue()
        maxsecy = self.search_controls.maxsecy_field.GetValue()
        maxsecz = self.search_controls.maxsecz_field.GetValue()
        centerx = self.search_controls.centerx_field.GetValue()
        centery = self.search_controls.centery_field.GetValue()
        centerz = self.search_controls.centerz_field.GetValue()
        radius = self.search_controls.radius_field.GetValue()

        def values_from_indices(l, indices):
            ret = []
            for i in indices:
                ret.append(l[i])
            return ret

        orbits = values_from_indices(orbit_zones, self.search_controls.orbit_field.GetSelections())
        bodies = values_from_indices(body_kinds, self.search_controls.body_field.GetSelections())

        if name+tl+planet+system+sector != '':
            rows = data.find_resources(exactname=name, mintl=tl, orbit_zones=orbits, body_kinds=bodies,
                                       planet=planet, system=system, sector=sector,
                                       minsecx=minsecx, minsecy=minsecy, minsecz=minsecz,
                                       maxsecx=maxsecx, maxsecy=maxsecy, maxsecz=maxsecz,
                                       centerx=centerx, centery=centery, centerz=centerz,
                                       radius=radius,
                                      )
            self.list.SetData(data.format_as_dict(rows))
            self.status.SetStatusText("%d resources found" % len(rows))

    def DefineDatabase(self, e):
        last_path = os.path.abspath(data.get_database_path())
        last_dir, last_file = os.path.split(last_path)
        dialog = wx.FileDialog(self, message="Please select the file you wish to use.",
                                     style=wx.FD_SAVE,
                                     defaultDir=last_dir,
                                     defaultFile=last_file,
                                     wildcard='Database files (*.sqlite3)|*.sqlite3|All files|*',
                                     )
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            data.set_database_path(path)
            self.status.SetStatusText("Database set to %s" % path)
        else:
            self.status.SetStatusText("Database unchanged (%s)" % last_path)

    def DefineMailcache(self, e):
        last_path = os.path.abspath(data.get_mailcache_path())
        dialog = wx.DirDialog(self, message="Please select the directory you wish to use.",
                                     style=wx.DD_DIR_MUST_EXIST,
                                     defaultPath=last_path,
                                     )
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            data.set_mailcache_path(path)
            self.status.SetStatusText("Mail Cache set to %s" % path)
        else:
            self.status.SetStatusText("Mail Cache unchanged (%s)" % last_path)

    def AddFile(self, e):
        dialog = wx.FileDialog(self, message="Please select the files you wish to process.", style=wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            paths = dialog.GetPaths()
            self.status.SetStatusText("Now processing %s files..." % len(paths))
            count = data.add_files(paths)
            self.status.SetStatusText("%s surveys added" % count)
        else:
            self.status.SetStatusText("no surveys added")

    def Update(self, e):
        mailcache_path = os.path.abspath(data.get_mailcache_path())
        self.status.SetStatusText("Now processing mail cache (%s)..." % mailcache_path)
        count = data.add_files_from_mailcache(mailcache_path)
        if count > 0:
            self.status.SetStatusText("%s surveys added" % count)
        else:
            self.status.SetStatusText("no surveys added")

    def ClearDatabase(self, e):
        self.status.SetStatusText("Clearing database...")
        data.drop_tables()
        self.status.SetStatusText("Database cleared")

    #def OnPaste(self, e):
    #    if not wx.TheClipboard.Open():
    #        #maybe it is already open, so close it and try again
    #        wx.TheClipboard.Close()
    #        if not wx.TheClipboard.Open():
    #            #give up
    #            self.status.SetStatusText("Could not open clipboard")
    #            return

    #    if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
    #        self.status.SetStatusText("Processing clipboard...")
    #        data_object = wx.TextDataObject()
    #        wx.TheClipboard.GetData(data_object)
    #        count = data.add_text(data_object.GetText())
    #        self.status.SetStatusText("%s surveys added from clipboard" % count)
    #    else:
    #        self.status.SetStatusText("Text is not supported by the clipboard")

    #    wx.TheClipboard.Close()

    def OnResize(self, e):
        #save the new dimensions
        wx.Config.Get().WriteInt('/window/width', e.GetSize()[0])
        wx.Config.Get().WriteInt('/window/height', e.GetSize()[1])

        #allow normal event code to run
        e.Skip()

    def ShowAbout(self, e):
        self.about.Show(True)

    def InitUI(self):
        self.SetTitle(version.fancy_name)
        if wx.Config.Get().HasEntry('/window/width'):
            size = (wx.Config.Get().ReadInt('/window/width'), wx.Config.Get().ReadInt('/window/height'))
        else:
            size = (1000, 400)
        self.SetSize(size)

        self.Bind(wx.EVT_SIZE, self.OnResize, self)


        #set up the menus
        self.menubar = Menubar(self)

        #set up the about window
        self.about = about.AboutWindow(self)


        #set up the panel
        panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(main_vbox)


        #add the toolbar
        self.toolbar = Toolbar(panel, self)
        main_vbox.Add(self.toolbar, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)


        #the main viewing area
        stuff = {
            0 : ('', '', '', '', '', '', '', '', '', '', '', ''),
            }
        self.list = ResultListCtrl(panel, stuff)
        main_vbox.Add(self.list, proportion=1, flag=wx.EXPAND)


        #add the search controls
        self.search_controls = SearchControls(panel, self)
        main_vbox.Add(self.search_controls, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)


        #the status bar
        self.status = wx.StatusBar(panel)
        self.status.SetFieldsCount(1)
        self.status.SetStatusStyles([wx.SB_FLAT])
        self.status.SetStatusText("Welcome to %s" % (version.fancy_string))
        main_vbox.Add(self.status, proportion=0, flag=wx.EXPAND, border=0)


        self.Show(True)

    def OnQuit(self, e):
        self.Close()

def main():
    Galactiscan(None)
