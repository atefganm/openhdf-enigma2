# -*- coding: utf-8 -*-
# by digiteng...12-2019

from os import path as os_path

from enigma import ePixmap, loadJPG

from Components.Renderer.Renderer import Renderer


class pstrRndr(Renderer):

	def __init__(self):
		Renderer.__init__(self)

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		try:
			eventName = self.source.text
			if eventName:
				poster = '/tmp/poster/poster.jpg'
				if os_path.exists(poster):
					self.instance.setPixmap(loadJPG(poster))
					self.instance.show()
				else:
					self.instance.hide()
			else:
				self.instance.hide()
		except:
			pass
