from abc import abstractmethod
from core.utils.log import *
import os
import pyautogui as gui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from time import sleep
import core.constants as constants
import pickle as pkl
import core.utils.monkey as monkey
from core.utils.IPManager import IPManager
from core.utils.log import debug, error, info, log
from core.constants import CHROME_VERSION

class BrowserFactory:
    _instance = None

    def __new__(cls, browser_type=None):
        if cls._instance is None:
            if browser_type is None:
                raise ValueError('Browser type must be specified')
            cls._instance = super().__new__(cls)
            cls._instance.browser_type = browser_type
        return cls._instance

    def getBrowser(self, session):
        if self.browser_type == 'uc_single':
            return UC_single_Browser(session)
        else:
            return UC_IP_Browser(session)

class Browser:
    @abstractmethod
    def getDriver(self):
        return self.driver

    def closeDriver(self):
        pass

    def forceCloseDriver(cls):
        cls._instance.driver.quit()
        cls._instance = None
        try:
            os.system("taskkill /f /im chrome.exe")
        except:
            pass
    
class UC_IP_Browser(Browser):
    _instance = None

    def __new__(cls, session):
        if cls._instance is None:
            info('Creating new instance of UC_IP_Browser')
            cls._instance = super().__new__(cls)
            cls._init_once(cls._instance, session)
        elif cls._instance.session != session:
            info('Recreating instance of UC_IP_Browser')
            cls._instance._closeDriver()
            sleep(10)
            cls._instance = super().__new__(cls)
            cls._init_once(cls._instance, session)
        else:
            info('Reusing instance of UC_IP_Browser')
        return cls._instance

    @classmethod
    def _init_once(cls, instance, session):
        from seleniumwire import undetected_chromedriver as seleniumwire_uc

        instance.session = session
        path = os.path.join(constants.SESSIONS_PATH, instance.session)
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-infobars")

        ip = IPManager.get_ip(instance.session)

        sw_options = {
            'proxy': {
                'https': f'https://{ip}'
            }
        }
        instance.driver = seleniumwire_uc.Chrome(user_data_dir=path, options=options, use_subprocess=False, seleniumwire_options=sw_options, version_main=CHROME_VERSION)
        sleep(4)
        monkey.GotIt()
        sleep(2)
        monkey.GotIt()
        sleep(1)
        monkey.remindMeLater()
        sleep(3)
        gui.hotkey('win', 'up')
        sleep(5)
        return 
    
    def _closeDriver(self):
        self.driver.quit()

class UC_single_Browser(Browser):
    _instance = None

    def __new__(cls, session):
        if cls._instance is None:
            debug('Making new browser.....')
            cls._instance = super().__new__(cls)
            cls._init_once(cls._instance, session)
        return cls._instance

    @classmethod
    def _init_once(cls, instance, session):
        instance.session = session
        path = os.path.join(constants.SESSIONS_PATH, instance.session)
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-infobars")
        
        instance.driver = uc.Chrome(user_data_dir=path, options=options, use_subprocess=False, version_main=CHROME_VERSION)
        sleep(4)
        monkey.GotIt()
        sleep(2)
        monkey.GotIt()
        sleep(1)
        monkey.remindMeLater()
        sleep(3)
        gui.hotkey('win', 'up')
        sleep(5)

    def closeDriver(self):
        pass