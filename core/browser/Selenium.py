from abc import abstractmethod
from core.utils.log import *
import os
import pyautogui as gui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from seleniumwire import undetected_chromedriver as seleniumwire_uc
from time import sleep
import core.constants as constants
import pickle as pkl
import core.utils.monkey as monkey
from core.utils.IPManager import IPManager

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

class UC_IP_Browser(Browser):
    def __init__(self, session):
        self.session = session
        path = os.path.join(constants.SESSIONS_PATH, self.session)
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-infobars")

        ip = IPManager.get_ip(self.session)

        sw_options = {
            'proxy': {
                'https': f'https://{ip}'
            }
        }
        self.driver = seleniumwire_uc.Chrome(user_data_dir=path, options=options, use_subprocess=False, seleniumwire_options=sw_options)
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

class UC_single_Browser(Browser):
    _instance = None

    def __new__(cls, session):
        if cls._instance is None:
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
        
        instance.driver = uc.Chrome(user_data_dir=path, options=options, use_subprocess=False, version_main=122)
        sleep(4)
        monkey.GotIt()
        sleep(2)
        monkey.GotIt()
        sleep(1)
        monkey.remindMeLater()
        sleep(3)
        gui.hotkey('win', 'up')
        sleep(5)

    def close_driver(self):
        pass
    