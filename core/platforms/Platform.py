import os
import sys

from core.utils.log import pprint, error, log
from core.utils.util import wait
from core.browser.Selenium import BrowserFactory
from core.utils.log import debug, info, error
from core.utils import monkey

import core.constants as constants

from abc import ABC, abstractclassmethod
from PIL import Image
import pyautogui as gui


class Platform(ABC):
    def __init__(self, platform, url, userId):
        self.platform = platform
        self.url = url
        self.userId = userId

    def loadBrowser(self):
        path = constants.SESSIONS_PATH
        if not os.path.exists(f'{path}{self.platform}'):
            os.mkdir(f'{path}{self.platform}')

        log(f'Loading browser for user: {self.userId}')
        id = self.userId
        path = os.path.join(constants.SESSIONS_PATH, id)

        if not os.path.exists(path):
            error(f'User {id} does not exist')
            os.mkdir(path)

        try:
            self.browser = BrowserFactory().getBrowser(id)
        except Exception as e:
            error(e)
            error('Could not load browser')
            debug('Trying again...')
            try:
                wait(3)
                self.browser = BrowserFactory().getBrowser(id)
            except Exception as e:
                error('Could not load browser again')
                raise e

        self.driver = self.browser.getDriver()
        return self.driver

    def loadWebsite(self):
        self.driver.get(self.url)

    def loadPage(self, url):
        self.driver.get(url)
    
    def chromeLogin(self):
        try:
            wait(1)
            screenWidth, screenHeight = gui.size()
            if screenWidth == 1920:
                monkey.click(x=1800, y=245)
            else:
                monkey.click(x=2300, y=230)
            return f'{self.userId}@spartaaceap.com'
        except Exception as e:
            print(e)
            return False
            pass

    def scrollTop(self):
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scrollDown(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    def searchTerm(self, term, bar=True):
        if bar:
            self._searchTermBar(term)
        else:
            self._searchTermUrl(term)

    def closeDriver(self):
        self.browser.closeDriver()

    @abstractclassmethod
    def loggedIn(self):
        pass
########################################################################################################################

# Search Platform
    @abstractclassmethod
    def _searchTermBar(self, term):
        pass

    @abstractclassmethod
    def _searchTermUrl(self, term):
        pass

# Navigate Platform   

    @abstractclassmethod
    def getHomePage(self):
        pass
    
# Interaction

    @abstractclassmethod
    def joinCommunity(self):
        pass

    @abstractclassmethod
    def followUser(self):
        pass

    @abstractclassmethod
    def openPost(self, already_opened=[]):
        pass

    @abstractclassmethod
    def likePost(self):
        pass

    @abstractclassmethod
    def getPagePosts(self, n=10):
        pass

    def TakeScreenshot(self, file):
        debug("Taking screenshot")
        self.driver.save_screenshot(file)
        debug(f'Screenshot saved: {file}')
        return True

    
    def screenshot(self, file):
        debug("Taking screenshot")
        self.driver.save_screenshot(file)
        debug(f'Screenshot saved: {file}')
        return True

    def fullScreenshot(self, file):
        debug("Taking screenshot")
        total_width = self.driver.execute_script("return document.body.offsetWidth")
        total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = self.driver.execute_script("return document.body.clientWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        rectangles = []

        # first go all the way up
        self.driver.execute_script("window.scrollTo(0, 0)")       

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height
            if top_height > total_height:
                top_height = total_height
            while ii < total_width:
                top_width = ii + viewport_width
                if top_width > total_width:
                    top_width = total_width
                rectangles.append((ii, i, top_width, top_height))
                ii += viewport_width
            i += viewport_height
        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0
        for rectangle in rectangles:
            if not previous is None:
                self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                wait(0.2)
            file_name = "part_{0}.png".format(part)
            self.driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)
            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])
            stitched_image.paste(screenshot, offset)
            del screenshot
            os.remove(file_name)
            part += 1
            previous = rectangle
        stitched_image.save(file)
        debug('Screenshot saved...')
        wait(1)
        self.driver.execute_script("window.scrollTo(0, 0)")       
        return True