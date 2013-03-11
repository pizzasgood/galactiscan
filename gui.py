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



class SearchControls(wx.BoxSizer):
    def __init__(self, parent):
        wx.BoxSizer.__init__(self, wx.VERTICAL)

        name_l = wx.StaticText(parent, label="Name")
        self.name_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        tl_l = wx.StaticText(parent, label="Min TL")
        self.tl_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        planet_l = wx.StaticText(parent, label="Planet")
        self.planet_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        system_l = wx.StaticText(parent, label="System")
        self.system_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)
        sector_l = wx.StaticText(parent, label="Sector")
        self.sector_field = wx.TextCtrl(parent, style=wx.TE_PROCESS_ENTER)

        self.search_button = wx.Button(parent, label="Search")

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.Add(hbox1, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)
        self.Add(hbox2, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)

        hbox1.Add(name_l,             proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.name_field,    proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(tl_l,               proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.tl_field,      proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox1.Add(self.search_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

        hbox2.Add(planet_l,             proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.planet_field,    proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(system_l,             proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.system_field,    proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(sector_l,             proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        hbox2.Add(self.sector_field,    proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)



    def GetNameFieldId(self):
        return self.name_field.GetId()

    def GetTlFieldId(self):
        return self.tl_field.GetId()

    def GetPlanetFieldId(self):
        return self.planet_field.GetId()

    def GetSystemFieldId(self):
        return self.system_field.GetId()

    def GetSectorFieldId(self):
        return self.sector_field.GetId()

    def GetSearchButtonId(self):
        return self.search_button.GetId()



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
        if name != '':
            rows = data.find_resources(name=name, mintl=tl, planet=planet, system=system, sector=sector)
            self.list.SetData(data.format_as_dict(rows))
            self.status.SetStatusText("%d resources found" % len(rows))

    def ClearDatabase(self, e):
        data.drop_tables()
        self.status.SetStatusText("Database cleared")

    def InitUI(self):
        self.SetTitle('Galactiscan')

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()

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


        #boxes to query name and tl
        self.search_controls = SearchControls(panel)
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=self.search_controls.GetSearchButtonId())
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, id=self.search_controls.GetNameFieldId())
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, id=self.search_controls.GetTlFieldId())
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, id=self.search_controls.GetPlanetFieldId())
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, id=self.search_controls.GetSystemFieldId())
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, id=self.search_controls.GetSectorFieldId())
        main_vbox.Add(self.search_controls, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)


        #the main viewing area
        stuff = {
            0 : ('', '', '', '', '', '', '', '', ''),
            }
        self.list = ResultListCtrl(panel, stuff)
        main_vbox.Add(self.list, proportion=1, flag=wx.EXPAND)


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

