
from Components.Element import Element
from Components.GUIComponent import GUIComponent


class Renderer(GUIComponent, Element):
	def __init__(self):
		Element.__init__(self)
		GUIComponent.__init__(self)

	def onShow(self):
		self.suspended = False

	def onHide(self):
		self.suspended = True
