
from os import path as os_path
from shutil import copy2, move, rmtree

from enigma import eTimer

from Components.Task import Job, PythonTask, Task
from Components.Task import job_manager as JobManager
from Tools.Directories import fileExists


class DeleteFolderTask(PythonTask):
	def openFiles(self, fileList):
		self.fileList = fileList

	def work(self):
		print("[DeleteFolderTask] files ", self.fileList)
		errors = []
		try:
			rmtree(self.fileList)
		except Exception as e:
			errors.append(e)
		if errors:
			raise errors[0]


class CopyFileJob(Job):
	def __init__(self, srcfile, destfile, name):
		Job.__init__(self, _("Copying files"))
		cmdline = 'cp -Rf "%s" "%s"' % (srcfile, destfile)
		AddFileProcessTask(self, cmdline, srcfile, destfile, name)


class MoveFileJob(Job):
	def __init__(self, srcfile, destfile, name):
		Job.__init__(self, _("Moving files"))
		cmdline = 'mv -f "%s" "%s"' % (srcfile, destfile)
		AddFileProcessTask(self, cmdline, srcfile, destfile, name)


class AddFileProcessTask(Task):
	def __init__(self, job, cmdline, srcfile, destfile, name):
		Task.__init__(self, job, name)
		self.setCmdline(cmdline)
		self.srcfile = srcfile
		self.destfile = destfile

		self.ProgressTimer = eTimer()
		self.ProgressTimer.callback.append(self.ProgressUpdate)

	def ProgressUpdate(self):
		if self.srcsize <= 0 or not fileExists(self.destfile, 'r'):
			return

		self.setProgress(int((os_path.getsize(self.destfile) / float(self.srcsize)) * 100))
		self.ProgressTimer.start(5000, True)

	def prepare(self):
		if fileExists(self.srcfile, 'r'):
			self.srcsize = os_path.getsize(self.srcfile)
			self.ProgressTimer.start(5000, True)

	def afterRun(self):
		self.setProgress(100)
		self.ProgressTimer.stop()


def copyFiles(fileList, name):
	for src, dst in fileList:
		if os_path.isdir(src) or int(os_path.getsize(src)) / 1000 / 1000 > 100:
			JobManager.AddJob(CopyFileJob(src, dst, name))
		else:
			copy2(src, dst)


def moveFiles(fileList, name):
	for src, dst in fileList:
		if os_path.isdir(src) or int(os_path.getsize(src)) / 1000 / 1000 > 100:
			JobManager.AddJob(MoveFileJob(src, dst, name))
		else:
			move(src, dst)


def deleteFiles(fileList, name):
	job = Job(_("Deleting files"))
	task = DeleteFolderTask(job, name)
	task.openFiles(fileList)
	JobManager.AddJob(job)
