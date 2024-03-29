# for localized messages

from Plugins.Plugin import PluginDescriptor

from . import _
from .HddMount import HddFastRemove
from .HddSetup import HddSetup


def deviceManagerMain(session, **kwargs):
	session.open(HddSetup)


def deviceManagerSetup(menuid, **kwargs):
	if menuid != "devices_menu":
		return []
	return [(_("Device Manager"), deviceManagerMain, "deviceManager", 5)]


def deviceManagerFastRemove(session, **kwargs):
	session.open(HddFastRemove)


def Plugins(**kwargs):
	return [PluginDescriptor(name=_("Device Manager"), description=_("Format/Partition your Devices and manage Mountpoints"), where=PluginDescriptor.WHERE_MENU, fnc=deviceManagerSetup),
			PluginDescriptor(name=_("Device Manager - Fast Mounted Remove"), description=_("Quick and safe remove for your mounted devices "), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=deviceManagerFastRemove)]
