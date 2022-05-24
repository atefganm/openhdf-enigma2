from __future__ import print_function
from __future__ import absolute_import
from Components.Task import job_manager, Job, PythonTask
from Components.config import config
from Components import Harddisk
from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText
from time import time
from os import path as os_path, access, W_OK, mkdir, walk, rmdir, statvfs, stat
from enigma import pNavigation, iRecordableService, eBackgroundFileEraser, eLabel


def getTrashFolder(path=None):
	# Returns trash folder without symlinks
	try:
		if path is None or os_path.realpath(path) == '/media/autofs':
			print('path is none')
			return ""
		else:
			if '/movie' in path:
				mountpoint = Harddisk.findMountPoint(os_path.realpath(path))
				trashcan = os_path.join(mountpoint, 'movie')
			else:
				trashcan = Harddisk.findMountPoint(os_path.realpath(path))
			return os_path.realpath(os_path.join(trashcan, ".Trash"))
	except:
		return None


def createTrashFolder(path=None):
	trash = getTrashFolder(path)
	if trash and access(os_path.split(trash)[0], W_OK):
		if not os_path.isdir(trash):
			try:
				mkdir(trash)
			except:
				return None
		return trash
	else:
		return None


def get_size(start_path='.'):
	total_size = 0
	if start_path:
		for dirpath, dirnames, filenames in walk(start_path):
			for f in filenames:
				try:
					fp = os_path.join(dirpath, f)
					total_size += os_path.getsize(fp)
				except:
					pass
	return total_size


class Trashcan:
	def __init__(self, session):
		self.session = session
		session.nav.record_event.append(self.gotRecordEvent)
		self.gotRecordEvent(None, None)

	def gotRecordEvent(self, service, event):
		self.recordings = len(self.session.nav.getRecordings(False, pNavigation.isRealRecording))
		if event == iRecordableService.evEnd:
			self.cleanIfIdle()

	def destroy(self):
		if self.session is not None:
			self.session.nav.record_event.remove(self.gotRecordEvent)
		self.session = None

	def __del__(self):
		self.destroy()

	def cleanIfIdle(self):
		# RecordTimer calls this when preparing a recording. That is a
		# nice moment to clean up.
		if self.recordings:
			print("[Trashcan] Recording in progress", self.recordings)
			return
		ctimeLimit = time() - (config.usage.movielist_trashcan_days.value * 3600 * 24)
		reserveBytes = 1024 * 1024 * 1024 * int(config.usage.movielist_trashcan_reserve.value)
		clean(ctimeLimit, reserveBytes)


def clean(ctimeLimit, reserveBytes):
	isCleaning = False
	for job in job_manager.getPendingJobs():
		jobname = str(job.name)
		if jobname.startswith(_("Cleaning Trashes")):
			isCleaning = True
			break

	if config.usage.movielist_trashcan.value and not isCleaning:
		name = _("Cleaning Trashes")
		job = Job(name)
		task = CleanTrashTask(job, name)
		task.openFiles(ctimeLimit, reserveBytes)
		job_manager.AddJob(job)
	elif isCleaning:
		print("[Trashcan] Cleanup already running")
	else:
		print("[Trashcan] Disabled skipping check.")


def cleanAll(path=None):
	trash = getTrashFolder(path)
	if not os_path.isdir(trash):
		print("[Trashcan] No trash.", trash)
		return 0
	for root, dirs, files in walk(trash, topdown=False):
		for name in files:
			fn = os_path.join(root, name)
			try:
				eBackgroundFileEraser.getInstance().erase(fn)
			except Exception as e:
				print("[Trashcan] Failed to erase %s:" % name, e)
		# Remove empty directories if possible
		for name in dirs:
			try:
				rmdir(os_path.join(root, name))
			except:
				pass


def init(session):
	global instance
	instance = Trashcan(session)


class CleanTrashTask(PythonTask):
	def openFiles(self, ctimeLimit, reserveBytes):
		self.ctimeLimit = ctimeLimit
		self.reserveBytes = reserveBytes

	def work(self):
		mounts = []
		matches = []
		print("[Trashcan] probing folders")
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if parts[1] == '/media/autofs':
				continue
			if config.usage.movielist_trashcan_network_clean.value and parts[1].startswith('/media/net'):
				mounts.append(parts[1])
			elif config.usage.movielist_trashcan_network_clean.value and parts[1].startswith('/media/autofs'):
				mounts.append(parts[1])
			elif not parts[1].startswith('/media/net') and not parts[1].startswith('/media/autofs'):
				mounts.append(parts[1])
		f.close()

		for mount in mounts:
			if os_path.isdir(os_path.join(mount, '.Trash')):
				matches.append(os_path.join(mount, '.Trash'))
			if os_path.isdir(os_path.join(mount, 'movie/.Trash')):
				matches.append(os_path.join(mount, 'movie/.Trash'))

		print("[Trashcan] found following trashcan's:", matches)
		if len(matches):
			for trashfolder in matches:
				print("[Trashcan] looking in trashcan", trashfolder)
				trashsize = get_size(trashfolder)
				diskstat = statvfs(trashfolder)
				free = diskstat.f_bfree * diskstat.f_bsize
				bytesToRemove = self.reserveBytes - free
				print("[Trashcan] " + str(trashfolder) + ": Size:", trashsize)
				candidates = []
				size = 0
				for root, dirs, files in walk(trashfolder, topdown=False):
					for name in files:
						try:
							fn = os_path.join(root, name)
							st = stat(fn)
							if st.st_ctime < self.ctimeLimit:
								eBackgroundFileEraser.getInstance().erase(fn)
								bytesToRemove -= st.st_size
							else:
								candidates.append((st.st_ctime, fn, st.st_size))
								size += st.st_size
						except Exception as e:
							print("[Trashcan] Failed to stat %s:" % name, e)
					# Remove empty directories if possible
					for name in dirs:
						try:
							rmdir(os_path.join(root, name))
						except:
							pass
					candidates.sort()
					# Now we have a list of ctime, candidates, size. Sorted by ctime (=deletion time)
					for st_ctime, fn, st_size in candidates:
						if bytesToRemove < 0:
							break
						try:
							# somtimes the file does not exist, can happen if trashcan is on a network, the main box could also be emptying trash at same time.
							eBackgroundFileEraser.getInstance().erase(fn)
						except:
							pass
						bytesToRemove -= st_size
						size -= st_size
					print("[Trashcan] " + str(trashfolder) + ": Size now:", size)


class TrashInfo(VariableText, GUIComponent):
	FREE = 0
	USED = 1
	SIZE = 2

	def __init__(self, path, type, update=True):
		GUIComponent.__init__(self)
		VariableText.__init__(self)
		self.type = type
		if update and path != '/media/autofs/':
			self.update(path)

	def update(self, path):
		try:
			total_size = get_size(getTrashFolder(path))
		except OSError:
			return -1

		if self.type == self.USED:
			try:
				if total_size < 10000000:
					total_size = _("%d KB") % (total_size >> 10)
				elif total_size < 10000000000:
					total_size = _("%d MB") % (total_size >> 20)
				else:
					total_size = _("%d GB") % (total_size >> 30)
				self.setText(_("Trashcan:") + " " + total_size)
			except:
				# occurs when f_blocks is 0 or a similar error
				self.setText("-?-")

	GUI_WIDGET = eLabel
