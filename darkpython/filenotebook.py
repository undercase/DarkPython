import wx, os
import wx.lib.agw.flatnotebook as fnb
from STCEdit import *
from debugger import *

class FileTextCtrl(MySTC):
	def __init__(self, filename, filedirectory, *args, **kwargs):
		MySTC.__init__(self, *args, **kwargs)
		self.SetMarginType(1, stc.STC_MARGIN_NUMBER)
		self.SetMarginWidth(1, 25)
		self.name = filename
		self.directory = filedirectory
		self.update()
	def save(self):
		file = open(os.path.join(self.directory, self.name), "w")
		file.write(self.GetText())
		print self.GetText()
		file.close()
	def save_as(self, filename, filedirectory):
		self.name = filename
		self.directory = filedirectory
		self.save()
	def update(self):
		# If the filename is untitled it's a temporary document which doesn't need to be updated
		if not self.name == "untitled":
			file = open(os.path.join(self.directory, self.name), "r")
			self.SetText(file.read())
			self.EmptyUndoBuffer()
			file.close()

class FileNotebook(fnb.FlatNotebook):
	def __init__(self, *args, **kwargs):
		fnb.FlatNotebook.__init__(self, *args, **kwargs)
		self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnClose, self)
		self.files = []
	def add_file(self, filename, filedirectory):
		self.files.append(FileTextCtrl(filename, filedirectory, parent=self))
		self.AddPage(self.files[-1], self.files[-1].name)
	def save_as(self, filename, filedirectory):
		self.files[self.GetSelection()].save_as(filename, filedirectory)
		self.SetPageText(self.GetSelection(), filename)
	def save(self):
		self.files[self.GetSelection()].save()
	def get_text(self):
		return self.files[self.GetSelection()].GetText()
	def interpret(self):
		if self.files[self.GetSelection()].name == "untitled":
			wx.MessageBox("You must save your file before running it!", "Info", wx.OK | wx.ICON_INFORMATION)
		else:
			os.system("python " + os.path.join(self.files[self.GetSelection()].directory, self.files[self.GetSelection()].name))
	def debug(self):
		if self.files[self.GetSelection()].name == "untitled":
			wx.MessageBox("You must save your file before debugging it!", "Info", wx.OK | wx.ICON_INFORMATION)
		else:
			#os.system("python -m pdb " + os.path.join(self.files[self.GetSelection()].directory, self.files[self.GetSelection()].name))
			debugger_window = DebuggerWindow(self.files[self.GetSelection()].GetText(), parent=None, title="Debugger", size=(640, 480))
	def get_selection(self):
		return self.files[self.GetSelection()]
	def OnClose(self, event):
		self.files.pop(self.GetSelection())