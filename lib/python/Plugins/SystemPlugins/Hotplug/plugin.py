# -*- coding: utf-8 -*-

from six import ensure_str
from twisted.internet.protocol import Factory, Protocol

from Components.Harddisk import harddiskmanager
from Plugins.Plugin import PluginDescriptor

hotplugNotifier = []


def processHotplugData(self, v):
	print("hotplug:", v)
	action = v.get("ACTION")
	device = v.get("DEVPATH")
	physdevpath = v.get("PHYSDEVPATH")
	media_state = v.get("X_E2_MEDIA_STATUS")

	dev = device.split('/')[-1]

	if action == "add":
		error, blacklisted, removable, is_cdrom, partitions, medium_found = harddiskmanager.addHotplugPartition(dev, physdevpath)
	elif action == "remove":
		harddiskmanager.removeHotplugPartition(dev)
	elif media_state is not None:
		if media_state == '1':
			harddiskmanager.removeHotplugPartition(dev)
			harddiskmanager.addHotplugPartition(dev, physdevpath)
		elif media_state == '0':
			harddiskmanager.removeHotplugPartition(dev)

	for callback in hotplugNotifier:
		try:
			callback(dev, action or media_state)
		except AttributeError:
			hotplugNotifier.remove(callback)


class Hotplug(Protocol):
	def __init__(self):
		pass

	def connectionMade(self):
		print("HOTPLUG connection!")
		self.received = ""

	def dataReceived(self, data):
		data = ensure_str(data)
		self.received += data
		print("complete", self.received)

	def connectionLost(self, reason):
		print("HOTPLUG connection lost!")
		data = self.received.split('\0')[:-1]
		v = {}
		for x in data:
			i = x.find('=')
			var, val = x[:i], x[i + 1:]
			v[var] = val
		processHotplugData(self, v)


def autostart(reason, **kwargs):
	if reason == 0:
		print("starting hotplug handler")
		import os

		from twisted.internet import reactor
		try:
			os.remove("/tmp/hotplug.socket")
		except OSError:
			pass
		factory = Factory()
		factory.protocol = Hotplug
		reactor.listenUNIX("/tmp/hotplug.socket", factory)


def Plugins(**kwargs):
	return PluginDescriptor(name="Hotplug", description="listens to hotplug events", where=PluginDescriptor.WHERE_AUTOSTART, needsRestart=True, fnc=autostart)
