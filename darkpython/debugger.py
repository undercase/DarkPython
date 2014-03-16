import bdb
import wx
import wx.grid
import threading
import thread
import sys

steps_lock = threading.Lock()
terminate = False
printing_functions = ["AppendText", "decode", "write"]
GRID_ARBITRARY = 45


class OutputRedir(object):
	def __init__(self, output):
		self.output = output
	def write(self, text):
		if not text == "" and not text == "\n":
			self.output.AppendText(str(text) + "\n")

class Debugger(bdb.Bdb, threading.Thread):
	"""
	This acts as a Debugger class for use in GUI's. Because it must run at the same time as a GUI and hang while waiting for input,
	it inherits from both the Basic Python Debugger (Bdb) and threading.Thread, making it multithreaded.

	On initialization, it takes in file-like objects (which support AppendText()) to write the output, and the current values of variables.

	It has locked variables that queue up button presses.

	It also keeps track of the last line executed and the line about to be executed. These lines are taken from frames.

	Because pythons threading module doesn't let you pass any arguments to run from start (and overriding start isn't really an option), the
	code to be debugged is passed to __init__.
	"""
	def __init__(self, output, variables, code, *args, **kwargs):
		bdb.Bdb.__init__(self)
		threading.Thread.__init__(self, *args, **kwargs)
		self.output = output
		self.variables = variables
		self.code = code
		self.steps = 0
		self.current_line = None
		self.next_line = None
		self.name = "Debugger Thread"
	def user_call(self, frame, argument_list):
		if frame.f_code.co_name in printing_functions:
			return
		self.output.AppendText(frame.f_code.co_name + " is about to be called\n")
	def user_line(self, frame):
		global steps_lock
		# Ignore printing functions (AppendText, Decode).These are side effects of redirecting to the output window.
		if not frame.f_code.co_name in printing_functions:
			while True:
				if terminate:
					thread.exit()
				if self.steps > 0:
					steps_lock.acquire(True)
					self.steps -= 1
					steps_lock.release()
					break
			#self.output.AppendText("Moving on to line " + str(frame.f_lineno) + "\n")
			self.current_line = self.next_line
			self.next_line = frame.f_lineno
		self.update_variables(frame)
	def user_return(self, frame, return_value):
		if frame.f_code.co_name in printing_functions:
			return
		self.output.AppendText(frame.f_code.co_name + " is about to return the value: " + str(return_value) + "\n")
	def user_exception(self, frame, exc_info):
		self.output.AppendText("An exception has occured on line " + str(exc_info[2].tb_lineno) + "\n")
	def update_variables(self, frame):
		if frame.f_code.co_name in printing_functions:
			return
		if not self.variables.GetNumberRows() == 0:
			self.variables.DeleteRows(numRows=self.variables.GetNumberRows())
		self.variables.AppendRows(numRows=len(frame.f_locals.keys()))
		for key in range(len(frame.f_locals.keys())):
			self.variables.SetCellValue(key, 0, str(frame.f_locals.keys()[key]))
			self.variables.SetCellValue(key, 1, str(frame.f_locals[frame.f_locals.keys()[key]]))
	def terminate(self):
		sys.exit()
	def run(self):
		if globals is None:
			import __main__
			globals = __main__.__dict__
		if locals is None:
			locals = globals
		self.reset()
		sys.settrace(self.trace_dispatch)
		if not isinstance(self.code, types.CodeType):
			self.code = self.code+'\n'
		try:
			exec self.code in globals, locals
		except BdbQuit:
			pass
		finally:
			self.quitting = 1
			sys.settrace(None)



class DebuggerWindow(wx.Frame):
	"""
	A Frame (Window) which acts as a debugger for a program.

	The layout will be as follows:
	**********************
	*               * VA *
	*     CODE      * RS *
	*               *    *
	**********************
	*CONT*    OUTPUT     *
	*ROLS*               *
	**********************

	It inherits from wx.Frame for the GUI.

	The code window is syntax highlighted and uneditable. The current line being executed
	is highlighted.

	The values of variables are displayed in the VARS window.

	The controls window houses buttons to control stepping through the program.

	The Output window displays output, showing when a function is about to be executed
	and when exceptions occur, etc.
	"""
	def __init__(self, code, *args, **kwargs):
		# Handle globals so the thread doesn't automatically try to terminate
		global terminate
		terminate = False
		wx.Frame.__init__(self, *args, **kwargs)
		self.SetIcon(wx.Icon("../assets/DarkPython.png", wx.BITMAP_TYPE_PNG))
		self.InitUI()
		self.debugger = Debugger(self.output, self.variables, code, name="Debugger thread!")
		self.code.AppendText(code)
		self.Show()
		self.debugger.start()
	def InitUI(self):
		# There will be one vertical sizer housing two horizontal sizers.
		panel = wx.Panel(self)
		vert_sizer = wx.BoxSizer(wx.VERTICAL)

		top_horz_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.code = wx.TextCtrl(panel, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
		top_horz_sizer.Add(self.code, proportion=2, flag=wx.EXPAND)
		self.variables = wx.grid.Grid(panel, id=wx.ID_ANY)
		self.variables.SetRowLabelSize(0)
		self.variables.SetColLabelSize(0)
		self.variables.CreateGrid(1, 2)
		top_horz_sizer.Add(self.variables, proportion=1, flag=wx.EXPAND)
		vert_sizer.Add(top_horz_sizer, proportion=2, flag=wx.EXPAND)

		bottom_horz_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.controls = wx.BoxSizer(wx.VERTICAL)
		self.step_button = wx.Button(panel, label="Step")
		self.Bind(wx.EVT_BUTTON, self.OnStep, self.step_button)
		self.controls.Add(self.step_button, flag=wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
		self.output = wx.TextCtrl(panel, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY)
		bottom_horz_sizer.Add(self.controls, flag=wx.LEFT | wx.RIGHT, border=10)
		bottom_horz_sizer.Add(self.output, proportion=1, flag=wx.EXPAND)
		vert_sizer.Add(bottom_horz_sizer, proportion=1, flag=wx.EXPAND)

		panel.SetSizer(vert_sizer)
		panel.SetAutoLayout(1)
		vert_sizer.Fit(panel)

		redir = OutputRedir(self.output)
		sys.stdout = redir

		# Update column sizes once the width of self.vars if finalized
		for col in range(self.variables.GetNumberCols()):
			self.variables.SetColSize(col, (self.variables.GetSizeTuple()[0] + GRID_ARBITRARY) / 2)

		# Bind close event
		self.Bind(wx.EVT_CLOSE, self.OnClose, self)
	def OnStep(self, event):
		global steps_lock
		steps_lock.acquire(True)
		self.debugger.steps += 1
		steps_lock.release()
		text = self.code.GetValue()
		text = text.split("\n")
		if not (self.debugger.next_line > len(text)):
			self.code.SetValue("")
			for line in range(len(text)):
				if text[line] == "":
					continue
				elif (line + 1) == self.debugger.next_line:
					self.code.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.GREEN))
					self.code.AppendText(text[line] + "\n")
				elif (line + 1) == self.debugger.current_line:
					self.code.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.RED))
					self.code.AppendText(text[line] + "\n")
				else:
					self.code.SetDefaultStyle(wx.TextAttr())
					self.code.AppendText(text[line] + "\n")
	def OnClose(self, event):
		global terminate
		terminate = True
		self.Destroy()
