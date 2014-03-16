#!/usr/bin/python
# -*- coding: utf-8 -*-

# gotoclass.py

import wx
import wx.stc as stc
import keyword
import os
import sys
import ConfigParser
from STCEdit import *
from filenotebook import *
import wx.lib.agw.flatnotebook as fnb

sys.stdout = open("stdout.log", "w")
sys.stderr = open("stderr.log", "w")

class DarkPython(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetIcon(wx.Icon("DarkPython.png", wx.BITMAP_TYPE_PNG))
        self.InitUI()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        vertsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.CreateStatusBar()
        menubar = wx.MenuBar()
        filemenu = wx.Menu()
        menunew = filemenu.Append(wx.ID_NEW, "&New", "Create a new file")
        menuopen = filemenu.Append(wx.ID_OPEN, "&Open", "Open a file for editing")
        menusave = filemenu.Append(wx.ID_SAVE, "&Save", "Save the current file")
        menusaveas = filemenu.Append(wx.ID_ANY, "SaveAs", "Save the current file with a specific filename")
        menuabout = filemenu.Append(wx.ID_ABOUT, "&About", "Information about DarkPython")
        menuexit = filemenu.Append(wx.ID_EXIT, "E&xit", "Close DarkPython")
        self.Bind(wx.EVT_MENU, self.OnNew, menunew)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuopen)
        self.Bind(wx.EVT_MENU, self.OnSave, menusave)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menusaveas)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuabout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuexit)
        menubar.Append(filemenu, "&File")
        runmenu = wx.Menu()
        menuinterpret = runmenu.Append(wx.ID_ANY, "&Interpret", "Use the python interpreter to run the program")
        menudebug = runmenu.Append(wx.ID_ANY, "&Debug", "Run the program with debug output")
        self.Bind(wx.EVT_MENU, self.OnInterpret, menuinterpret)
        self.Bind(wx.EVT_MENU, self.OnDebug, menudebug)
        menubar.Append(runmenu, "&Run")
        settingsmenu = wx.Menu()
        menupython = settingsmenu.Append(wx.ID_ANY, "&Python", "Configure python settings")
        self.Bind(wx.EVT_MENU, self.OnPython, menupython)
        menubar.Append(settingsmenu, "&Settings")
        self.SetMenuBar(menubar)

        toolbar = self.CreateToolBar()
        interprettool = toolbar.AddLabelTool(wx.ID_ANY, "Interpret", wx.Bitmap("interpret.png"))
        debugtool = toolbar.AddLabelTool(wx.ID_ANY, "Debug", wx.Bitmap("debug.png"))
        savetool = toolbar.AddLabelTool(wx.ID_ANY, "Save", wx.Bitmap("save.png"))
        newtool = toolbar.AddLabelTool(wx.ID_ANY, "New File", wx.Bitmap("newfile.png"))
        opentool = toolbar.AddLabelTool(wx.ID_ANY, "Open File", wx.Bitmap("open.png"))
        toolbar.Realize()
        self.Bind(wx.EVT_TOOL, self.OnInterpret, interprettool)
        self.Bind(wx.EVT_TOOL, self.OnDebug, debugtool)
        self.Bind(wx.EVT_TOOL, self.OnSave, savetool)
        self.Bind(wx.EVT_TOOL, self.OnNew, newtool)
        self.Bind(wx.EVT_TOOL, self.OnOpen, opentool)

        self.notebook = FileNotebook(panel, agwStyle=fnb.FNB_NO_X_BUTTON | fnb.FNB_NO_NAV_BUTTONS | fnb.FNB_X_ON_TAB)
        self.notebook.add_file("untitled", "")
        vertsizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)

        """self.textcontrol = MySTC(self.notebook)
        self.textcontrol.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.textcontrol.SetMarginWidth(1, 25)
        self.notebook.AddPage(self.textcontrol, "untitled")
        vertsizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)"""

        panel.SetSizer(vertsizer)
        panel.SetAutoLayout(1)
        vertsizer.Fit(panel)

    def OnNew(self, event):
        self.notebook.add_file("untitled", "")

    def OnOpen(self, event):
        dialog = wx.FileDialog(self, "Choose the file you want to edit", "", "", "*.*", wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.notebook.add_file(dialog.GetFilename(), dialog.GetDirectory())
        dialog.Destroy()

    def OnSave(self, event):
        self.notebook.save()

    def OnSaveAs(self, event):
        selection = self.notebook.get_selection()
        dialog = wx.FileDialog(self, "Choose what you want to save the file as", selection.directory, selection.name, "*.*", wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.notebook.save_as(dialog.GetFilename(), dialog.GetDirectory())
        dialog.Destroy()

    def OnAbout(self, event):
        description = """DarkPython is an open-source program for Windows,
Mac, and Linux. It was made to make it easier and more fun to teach
python in the school environment. As a backbone, wxWidgets and Pygame
are used!"""
        licence = """DarkPython is free and open source. You can redist ribute
it and / or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2 of the
license, or (at your option) any later version.

DarkPython is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details."""
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon("DarkPython.png", wx.BITMAP_TYPE_PNG))
        info.SetName("DarkPython")
        info.SetVersion("Alpha")
        info.SetDescription(description)
        info.SetCopyright("(C) 2014 Thomas Hobohm")
        info.SetWebSite("http://www.darkpython.org")
        info.SetLicence(licence)
        info.AddDeveloper("Thomas Hobohm")
        wx.AboutBox(info)

    def OnExit(self, event):
        self.Close()

    #OnRun and OnDebug are being left for once I start integrating with the python interpreter.
    def OnInterpret(self, event):
        self.notebook.interpret()

    def OnDebug(self, event):
        self.notebook.debug()

    def OnPython(self, event):
        dialog = wx.TextEntryDialog(self, "Where is your python path?", caption="Python Path")
        if dialog.ShowModal() == wx.ID_OK:
            pythonpath = dialog.GetValue()
            file = open("settings.ini", "w")
            config = ConfigParser.ConfigParser()
            config.add_section("python")
            config.set("python", "path", pythonpath)
            config.write(file)
            file.close()
        dialog.Destroy()

class DebugDialog(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.InitUI()

app = wx.App(redirect=True, filename="logfile.txt")
window = DarkPython(parent=None, title="DarkPython", size=(800, 640))
app.MainLoop()