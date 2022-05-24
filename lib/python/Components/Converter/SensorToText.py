from __future__ import absolute_import
from Components.Converter.Converter import Converter
from six import PY3

SIGN = '°' if PY3 else str('\xc2\xb0')


class SensorToText(Converter):
	def __init__(self, arguments):
		Converter.__init__(self, arguments)

	def getText(self):
		if self.source.value is None:
			return ""
		unit = self.source.getUnit()
		if unit in ('C', 'F'):
			return "%d%s%s" % (self.source.getValue(), SIGN, unit)

	text = property(getText)
