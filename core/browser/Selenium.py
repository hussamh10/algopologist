from abc import abstractmethod
import shutil
from core.utils.log import *
import os
import pyautogui as gui
from core.utils.util import wait
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
        # del cls._instance.driver
        cls._instance = None
        try:
            os.system("taskkill /f /im chrome.exe")
        except Exception as e:
            print
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
        
        instance.driver = uc.Chrome(user_data_dir=path, options=options, use_subprocess=False)
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



class SimpleBrowser(Browser):
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
        
        instance.driver = uc.Chrome(user_data_dir=path, options=options, use_subprocess=False)
        sleep(4)
        monkey.GotIt()
        sleep(2)
        monkey.GotIt()
        sleep(1)
        monkey.remindMeLater()
        sleep(3)
        gui.hotkey('win', 'up')
        sleep(5)

    def _init_again(self):
        path = os.path.join(constants.SESSIONS_PATH, self.session)
        options = uc.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-infobars")
        
        self.driver = uc.Chrome(user_data_dir=path, options=options, use_subprocess=False)
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

    def delete_folder(self, folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"Folder '{folder_path}' deleted successfully.")
        except FileNotFoundError:
            print(f"Folder '{folder_path}' not found.")
        except OSError as e:
            print(f"Error deleting...")

    
    def copy_folder(self, source, dest):
        try:
            shutil.copytree(source, dest)
            print(f"Folder '{source}' copied to '{dest}'")
        except FileNotFoundError:
            print(f"Source folder '{source}' not found.")
        except FileExistsError:
            print(f"Destination folder '{dest}' already exists.")
        except shutil.Error as e:
            print(f"Error copying...")

    def saveProfile(self):
        path = os.path.join(constants.SESSIONS_PATH, self.session)
        print(path)
        orginal_path = path + '_original'
        if os.path.exists(orginal_path):
            self.delete_folder(orginal_path)

        self.copy_folder(path, orginal_path)
        

    def refreshProfile(self):
        path = os.path.join(constants.SESSIONS_PATH, self.session)
        print(path)
        orginal_path = path + '_original'
        if os.path.exists(orginal_path):
            self.delete_folder(path)
            self.copy_folder(orginal_path, path)

    def refreshBrowser(self, clean=False):
        # close()
        self.driver.quit()
        del self.driver
        try:
            os.system("taskkill /f /im chrome.exe")
            print('Chrome killed...')
        except Exception as e:
            print('Cannot kill chrome...')
            pass
        wait(50)

        if clean:
            self.refreshProfile()

        self._init_again()

    def forceCloseDriver(self):
        self.driver.quit()
        del self.driver
        wait(20)
        try:
            os.system("taskkill /f /im chrome.exe")
            print('Chrome killed...')
        except Exception as e:
            print('Cannot kill chrome...')
            pass
        
        wait(20)