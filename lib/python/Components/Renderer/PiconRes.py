
from os import listdir
from os import path as os_path

from enigma import ePicLoad, ePixmap

from Components.Harddisk import harddiskmanager
from Components.Renderer.Renderer import Renderer
from Tools.Alternatives import GetWithAlternative
from Tools.Directories import (SCOPE_GUISKIN, SCOPE_SKIN_IMAGE, pathExists,
                               resolveFilename)

searchPaths = []
lastPiconPath = None


def initPiconPaths():
	global searchPaths
	searchPaths = []
	for mp in ('/usr/share/enigma2/', '/'):
		onMountpointAdded(mp)
	for part in harddiskmanager.getMountedPartitions():
		mp = path = os_path.join(part.mountpoint, 'usr/share/enigma2')
		onMountpointAdded(part.mountpoint)
		onMountpointAdded(mp)


def onMountpointAdded(mountpoint):
	global searchPaths
	try:
		path = os_path.join(mountpoint, 'picon') + '/'
		if os_path.isdir(path) and path not in searchPaths:
			for fn in listdir(path):
				if fn.endswith('.png'):
					print("[Picon] adding path:", path)
					searchPaths.append(path)
					break
	except Exception as ex:
		print("[Picon] Failed to investigate %s:" % mountpoint, ex)


def onMountpointRemoved(mountpoint):
	global searchPaths
	path = os_path.join(mountpoint, 'picon') + '/'
	try:
		searchPaths.remove(path)
		print("[Picon] removed path:", path)
	except:
		pass


def onPartitionChange(why, part):
	if why == 'add':
		onMountpointAdded(part.mountpoint)
	elif why == 'remove':
		onMountpointRemoved(part.mountpoint)


def findPicon(serviceName):
	global lastPiconPath
	if lastPiconPath is not None:
		pngname = lastPiconPath + serviceName + ".png"
		if pathExists(pngname):
			return pngname
		else:
			return ""
	else:
		global searchPaths
		pngname = ""
		for path in searchPaths:
			if pathExists(path) and not path.startswith('/media/net'):
				pngname = path + serviceName + ".png"
				if pathExists(pngname):
					lastPiconPath = path
					break
			elif pathExists(path):
				pngname = path + serviceName + ".png"
				if pathExists(pngname):
					lastPiconPath = path
					break
		if pathExists(pngname):
			return pngname
		else:
			return ""


def getPiconName(serviceName):
	sname = '_'.join(GetWithAlternative(serviceName).split(':', 10)[:10])
	pngname = findPicon(sname)
	if not pngname:
		fields = sname.split('_', 3)
		if len(fields) > 0 and fields[0] != '1':
			fields[0] = '1'
		pngname = findPicon('_'.join(fields))
	return pngname


class PiconRes(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.PicLoad = ePicLoad()
		self.PicLoad.PictureData.get().append(self.updatePicon)
		self.piconsize = (0, 0)
		self.pngname = ""
		self.lastPath = None
		pngname = findPicon("picon_default")
		self.defaultpngname = None
		if not pngname:
			tmp = resolveFilename(SCOPE_GUISKIN, "picon_default.png")
			if pathExists(tmp):
				pngname = tmp
			else:
				pngname = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
		self.nopicon = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
		if os_path.getsize(pngname):
			self.defaultpngname = pngname
			self.nopicon = pngname

	def addPath(self, value):
		if pathExists(value):
			global searchPaths
			if not value.endswith('/'):
				value += '/'
			if value not in searchPaths:
				searchPaths.append(value)

	def applySkin(self, desktop, parent):
		attribs = self.skinAttributes[:]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				self.addPath(value)
				attribs.remove((attrib, value))
			elif attrib == "size":
				self.piconsize = value
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def postWidgetCreate(self, instance):
		self.changed((self.CHANGED_DEFAULT,))

	def updatePicon(self, picInfo=None):
		ptr = self.PicLoad.getData()
		if ptr != None:
			self.instance.setPixmap(ptr.__deref__())
			self.instance.show()

	def changed(self, what):
		if self.instance:
			pngname = ""
			if what[0] == 1 or what[0] == 3:
				pngname = getPiconName(self.source.text)
				if not pathExists(pngname): # no picon for service found
					pngname = self.defaultpngname
				if self.pngname != pngname:
					if pngname:
						self.PicLoad.setPara((self.piconsize[0], self.piconsize[1], 0, 0, 1, 1, "#FF000000"))
						self.PicLoad.startDecode(pngname)
					else:
						self.instance.hide()
					self.pngname = pngname


harddiskmanager.on_partition_list_change.append(onPartitionChange)
initPiconPaths()
