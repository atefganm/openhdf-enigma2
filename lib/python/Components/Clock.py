
from time import localtime

from enigma import eLabel, eTimer

from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText

# now some "real" components:


class Clock(VariableText, GUIComponent):
	def __init__(self):
		VariableText.__init__(self)
		GUIComponent.__init__(self)
		self.doClock()

		self.clockTimer = eTimer()
		self.clockTimer.callback.append(self.doClock)

	def onShow(self):
		self.doClock()
		self.clockTimer.start(1000)

	def onHide(self):
		self.clockTimer.stop()

	def doClock(self):
		t = localtime()
		timestr = "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
		self.setText(timestr)

	def createWidget(self, parent):
		return eLabel(parent)

	def removeWidget(self, w):
		del self.clockTimer
