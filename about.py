#!/usr/bin/python2
import wx

import version

class InfoTab(wx.ScrolledWindow):
    def __init__(self, parent):
        super(InfoTab, self).__init__(parent)
        self.SetScrollRate(5,5)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        name = wx.StaticText(self, label=version.fancy_string)
        description = wx.StaticText(self, label=version.description)
        url = wx.HyperlinkCtrl(self, wx.ID_ANY, label=version.url, url=version.url)
        copyright = wx.StaticText(self, label=version.copyright)

        default_fontsize = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPointSize()

        title_font = wx.Font(default_fontsize+2, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        copyright_font = wx.Font(default_fontsize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)

        name.SetFont(title_font)
        copyright.SetFont(copyright_font)

        description.Wrap(400)

        vbox.Add(name,        proportion=0, flag=wx.ALIGN_CENTER|wx.TOP, border=10)
        vbox.Add(description, proportion=0, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        vbox.Add(url,         proportion=0, flag=wx.ALIGN_CENTER|wx.TOP, border=10)
        vbox.Add(copyright,   proportion=0, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)





class LicenseTab(wx.ScrolledWindow):
    def __init__(self, parent):
        super(LicenseTab, self).__init__(parent)
        self.SetScrollRate(5,5)

        vbox = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(self, label=version.getLicenseBody())

        self.SetSizer(vbox)
        vbox.Add(text, proportion=0, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, border=10)


class AboutWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(AboutWindow, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

        self.SetTitle("About %s" % (version.fancy_name))

        tabs = wx.Notebook(self)

        info_tab = InfoTab(tabs)
        tabs.AddPage(info_tab, 'Info')
        license_tab = LicenseTab(tabs)
        tabs.AddPage(license_tab, 'License')

    def OnClose(self, e):
        if e.CanVeto():
            self.Show(False)
            e.Veto()
        else:
            self.Destroy()

