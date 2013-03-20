#!/usr/bin/python2
# vim: ts=4 : sts=4 : sw=4 : et :

import sqlite3
import datetime
import os.path
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ColumnSorterMixin

import survey
import data



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
        self.InsertColumn(3, 'prev', wx.LIST_FORMAT_RIGHT, 40)
        self.InsertColumn(4, 'type', width=80)
        self.InsertColumn(5, 'zone', width=50)
        self.InsertColumn(6, 'world', width=140)
        self.InsertColumn(7, 'system', width=140)
        self.InsertColumn(8, 'sector', width=140)
        self.InsertColumn(9, 'coords', width=80)

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



class Toolbar(wx.BoxSizer):
    def __init__(self, parent, grandparent):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        #create the buttons
        self.open_button = wx.Button(parent, id=wx.ID_OPEN, style=wx.BU_EXACTFIT)
        self.clear_button = wx.Button(parent, id=wx.ID_CLEAR, style=wx.BU_EXACTFIT)

        #add the buttons to the widget
        self.Add(self.open_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT)
        self.Add(self.clear_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT)

        #bind the buttons to actions
        grandparent.Bind(wx.EVT_BUTTON, grandparent.OpenFile,  id=self.open_button.GetId())
        grandparent.Bind(wx.EVT_BUTTON, grandparent.ClearDatabase,  id=self.clear_button.GetId())



class SearchControls(wx.BoxSizer):
    def __init__(self, parent, grandparent):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        name_l = wx.StaticText(parent, label="Name:")
        self.name_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        tl_l = wx.StaticText(parent, label="Min TL:")
        self.tl_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
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

        self.reset_button = wx.Button(parent, label="Reset")
        self.search_button = wx.Button(parent, label="Search")

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_coords_ls = wx.BoxSizer(wx.VERTICAL)
        vbox_coords = wx.BoxSizer(wx.VERTICAL)
        vbox_radius = wx.BoxSizer(wx.VERTICAL)
        hbox_minsec = wx.BoxSizer(wx.HORIZONTAL)
        hbox_maxsec = wx.BoxSizer(wx.HORIZONTAL)
        hbox_center = wx.BoxSizer(wx.HORIZONTAL)
        hbox_radius = wx.BoxSizer(wx.HORIZONTAL)

        self.Add(hbox1, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)
        self.Add(hbox2, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)
        self.Add(hbox3, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)

        hbox3.Add(vbox_coords_ls, proportion=0, flag=wx.LEFT, border=5)
        hbox3.Add(vbox_coords,    proportion=1)
        hbox3.Add(vbox_radius,    proportion=2)

        vbox_coords.Add(hbox_minsec, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)
        vbox_coords.Add(hbox_maxsec, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)
        vbox_radius.Add(hbox_center, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)
        vbox_radius.Add(hbox_radius, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND)

        hbox1.Add(name_l,            proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.name_field,   proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(tl_l,              proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.tl_field,     proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox2.Add(planet_l,          proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.planet_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(system_l,          proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.system_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(sector_l,          proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.sector_field, proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        vbox_coords_ls.Add(minsec_l, proportion=1, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
        vbox_coords_ls.Add(maxsec_l, proportion=1, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)

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
        hbox_radius.Add(self.radius_field,  proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_radius.Add(self.reset_button,  proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox_radius.Add(self.search_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

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
        if name+tl+planet+system+sector != '':
            rows = data.find_resources(name=name, mintl=tl,
                                       planet=planet, system=system, sector=sector,
                                       minsecx=minsecx, minsecy=minsecy, minsecz=minsecz,
                                       maxsecx=maxsecx, maxsecy=maxsecy, maxsecz=maxsecz,
                                       centerx=centerx, centery=centery, centerz=centerz,
                                       radius=radius,
                                      )
            self.list.SetData(data.format_as_dict(rows))
            self.status.SetStatusText("%d resources found" % len(rows))

    def OpenFile(self, e):
        dialog = wx.FileDialog(self, message="Please select the files you wish to load.", style=wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            paths = dialog.GetPaths()
            self.status.SetStatusText("Now loading %s files..." % len(paths))
            data.add_files(paths)
            self.status.SetStatusText("%s files loaded" % len(paths))
        else:
            self.status.SetStatusText("no files loaded")

    def ClearDatabase(self, e):
        self.status.SetStatusText("Clearing database...")
        data.drop_tables()
        self.status.SetStatusText("Database cleared")

    def InitUI(self):
        self.SetTitle('Galactiscan')

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()

        fitem = fileMenu.Append(wx.ID_OPEN, 'Open', 'Open File(s)')
        self.Bind(wx.EVT_MENU, self.OpenFile, fitem)

        fitem = fileMenu.Append(wx.ID_CLEAR, 'Clear DB', 'Clear database')
        self.Bind(wx.EVT_MENU, self.ClearDatabase, fitem)

        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)


        #set up the panel
        panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(main_vbox)


        #add the toolbar
        self.toolbar = Toolbar(panel, self)
        main_vbox.Add(self.toolbar, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)


        #the main viewing area
        stuff = {
            0 : ('', '', '', '', '', '', '', '', '', ''),
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
        self.status.SetStatusText("Welcome to Galactiscan")
        main_vbox.Add(self.status)


        self.Show(True)

    def OnQuit(self, e):
        self.Close()

def main():
    gs = wx.App()
    Galactiscan(None)
    gs.MainLoop()

