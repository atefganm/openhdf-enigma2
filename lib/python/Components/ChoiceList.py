
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont

from Components.MenuList import MenuList
from skin import fonts, parameters
from Tools.Directories import SCOPE_GUISKIN, fileExists, resolveFilename
from Tools.LoadPixmap import LoadPixmap


def row_delta_y():
	font = fonts["ChoiceList"]
	return (int(font[2]) - int(font[1])) / 2


def ChoiceEntryComponent(key=None, text=["--"]):
	res = [text]
	if text[0] == "--":
		x, y, w, h = parameters.get("ChoicelistDash", (0, 2, 800, 25))
		res.append((eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 0, RT_HALIGN_LEFT, "-" * 200))
	else:
		x, y, w, h = parameters.get("ChoicelistName", (45, 2, 800, 25))
		res.append((eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 0, RT_HALIGN_LEFT, text[0]))
		if key:
			if key == "expandable":
				pngfile = resolveFilename(SCOPE_GUISKIN, "icons/expandable.png")
			elif key == "expanded":
				pngfile = resolveFilename(SCOPE_GUISKIN, "icons/expanded.png")
			elif key == "verticalline":
				pngfile = resolveFilename(SCOPE_GUISKIN, "icons/verticalline.png")
			elif key == "bullet":
				pngfile = resolveFilename(SCOPE_GUISKIN, "icons/bullet.png")
			else:
				pngfile = resolveFilename(SCOPE_GUISKIN, "buttons/key_%s.png" % key)
			if fileExists(pngfile):
				png = LoadPixmap(pngfile)
				x, y, w, h = parameters.get("ChoicelistIcon", (5, 0, 35, 25))
				res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x, y, w, h, png))
	return res


class ChoiceList(MenuList):
	def __init__(self, list, selection=0, enableWrapAround=False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		font = fonts.get("ChoiceList", ("Regular", 20, 30))
		self.l.setFont(0, gFont(font[0], font[1]))
		self.l.setItemHeight(font[2])
		self.ItemHeight = font[2]
		self.selection = selection

	def postWidgetCreate(self, instance):
		MenuList.postWidgetCreate(self, instance)
		self.moveToIndex(self.selection)
		self.instance.setWrapAround(True)

	def getItemHeight(self):
		return self.ItemHeight
