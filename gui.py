#!/usr/bin/python2
# vim: ts=4 : sts=4 : sw=4 : et :

import sqlite3
import datetime
import os.path
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ColumnSorterMixin

import Survey
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
        self.InsertColumn(1, 'tl', wx.LIST_FORMAT_RIGHT, 40)
        self.InsertColumn(2, 'quality', wx.LIST_FORMAT_RIGHT, 60)
        self.InsertColumn(3, 'prev', wx.LIST_FORMAT_RIGHT, 40)
        self.InsertColumn(4, 'type', width=80)
        self.InsertColumn(5, 'system', width=140)
        self.InsertColumn(6, 'world', width=140)

        #insert the data
        items = data.items()
        for key, i in items:
            index = self.InsertStringItem(sys.maxint, i[0])
            for k in range(1, len(i)):
                self.SetStringItem(index, k, i[k])
            self.SetItemData(index, key)



class SearchControls(wx.BoxSizer):
    def __init__(self, parent):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        name_l = wx.StaticText(parent, label="Name")
        self.name_field = wx.TextCtrl(parent)
        tl_l = wx.StaticText(parent, label="TL")
        self.tl_field = wx.TextCtrl(parent)
        self.search_button = wx.Button(parent, label="Search")

        self.Add(name_l,             proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        self.Add(self.name_field,    proportion=1, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        self.Add(tl_l,               proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        self.Add(self.tl_field,      proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)
        self.Add(self.search_button, proportion=0, flag=wx.ALIGN_CENTER|wx.LEFT|wx.RIGHT, border=5)

    def GetSearchButtonId(self):
        return self.search_button.GetId()



class Galactiscan(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Galactiscan, self).__init__(*args, **kwargs)

        self.InitUI()

    def OnSearch(self, e):
        name = self.search_controls.name_field.GetValue()
        tl = self.search_controls.tl_field.GetValue()
        rows = data.find_resources_by_name(name, tl)
        data.display_rows(rows)

    def InitUI(self):
        self.SetTitle('Galactiscan')

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)


        #set up the panel
        panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(main_vbox)


        #boxes to query name and tl
        self.search_controls = SearchControls(panel)
        self.Bind(wx.EVT_BUTTON, self.OnSearch, id=self.search_controls.GetSearchButtonId())
        main_vbox.Add(self.search_controls, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=0)


        #the main viewing area
        stuff = {
            1 : ('Antiflux Particles', 'TL29', 'Q228', '4%', 'Ring', 'Demo System', 'Demo IIbr'),
            2 : ('Antiflux Particles', 'TL10', 'Q82', '1%', 'Planet', 'Demo System', 'Demo I'),
            }
        self.list = ResultListCtrl(panel, stuff)
        main_vbox.Add(self.list, 1, wx.EXPAND)


        self.Show(True)

    def OnQuit(self, e):
        self.Close()

def main():
    gs = wx.App()
    Galactiscan(None)
    gs.MainLoop()

