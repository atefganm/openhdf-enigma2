
from boxbranding import getBoxType

from Components.config import ConfigBoolean, config, configfile
from Components.Pixmap import Pixmap
from Screens.LanguageSelection import LanguageWizard
from Screens.Rc import Rc
from Screens.Screen import Screen
from Screens.VideoWizard import VideoWizard
from Screens.Wizard import wizardManager
from Screens.WizardLanguage import WizardLanguage
from Screens.WizardUserInterfacePositioner import UserInterfacePositionerWizard

config.misc.firstrun = ConfigBoolean(default=True)
config.misc.languageselected = ConfigBoolean(default=True)
config.misc.videowizardenabled = ConfigBoolean(default=True)


class StartWizard(WizardLanguage, Rc):
	def __init__(self, session, silent=True, showSteps=False, neededTag=None):
		self.xmlfile = ["startwizard.xml"]
		WizardLanguage.__init__(self, session, showSteps=False)
		Rc.__init__(self)
		self["wizard"] = Pixmap()
		Screen.setTitle(self, _("Welcome..."))

	def markDone(self):
		# setup remote control, all stb have same settings except dm8000 which uses a different settings
		if getBoxType() == 'dm8000':
			config.misc.rcused.value = 0
		else:
			config.misc.rcused.value = 1
		config.misc.rcused.save()

		config.misc.firstrun.value = 0
		config.misc.firstrun.save()
		configfile.save()


wizardManager.registerWizard(LanguageWizard, config.misc.languageselected.value, priority=0)
wizardManager.registerWizard(VideoWizard, config.misc.videowizardenabled.value, priority=1)
wizardManager.registerWizard(UserInterfacePositionerWizard, config.misc.firstrun.value, priority=2)
wizardManager.registerWizard(StartWizard, config.misc.firstrun.value, priority=20)
