import sys

from core.utils.util import wait; sys.path.append('..')
from core.platforms.Platform import Platform
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from core.utils.log import *
from time import sleep
import core.constants as constants
from core.utils import monkey

# REQUIRED CAPTCHA!
# https://piprogramming.org/articles/How-to-make-Selenium-undetectable-and-stealth--7-Ways-to-hide-your-Bot-Automation-from-Detection-0000000017.html

import constants

class TikTok(Platform):
    name = 'tiktok'
    url='https://www.tiktok.com'
    signin_url='https://www.tiktok.com/login'
    search_url='https://www.tiktok.com/search/user?q=%s'
    # Tiktok also adds the timestamp in front of the search like this: https://www.tiktok.com/search/user?q=abortion&t=1646274640529

    def __init__(self, user):
        super().__init__(TikTok.name, TikTok.url, user)

    def _searchTermUrl(self, term):
        search_query = TikTok.search_url % (term)
        self.loadPage(search_query)

    def _searchTermBar(self, term):
        search_bar = self._getSearchBar()
        print(search_bar)
        search_bar.send_keys(term)
        sleep(1)
        search_bar.send_keys(Keys.ENTER)

    def _getSearchBar(self):
        search = self.driver.find_element(By.XPATH, '//input[@aria-label="Search"]')
        return search
    
    def _searchTermBar(self, term):
        pass

    def _searchTermUrl(self, term):
        pass


    def chromeLogin(self):
        info('TikTok login')
        self.driver.get(self.signin_url)
        wait(2)

        # select signin with Google

        btn = self.driver.find_element(By.XPATH, "//p[contains(text(), 'Continue with Google')]")
        btn.click()
        wait(3)
        monkey.next()
        monkey.next()
        monkey.enter()
        wait(2)

        # enter date of birth

        monkey.next()
        monkey.type('jan')
        monkey.enter()

        monkey.next()
        monkey.type('22')
        monkey.enter()

        monkey.next()
        monkey.enter()
        monkey.type('1995')
        monkey.enter()

        monkey.next()
        monkey.enter()





# Navigate Platform   

    def createUser(self):
        pass

    def getHomePage(self):
        self.driver.get("https://www.tiktok.com/foryou?lang=en")
        pass
    
# Interaction

    def joinCommunity(self):
        pass

    def followUser(self):
        pass

    def readComments(self):
        pass

    def openPost(self, already_opened=[]):
        pass

    def stayOnPost(self, time=5):
        sleep(time)

    # @abstractclassmethod
    def likePost(self):
        pass

    # @abstractclassmethod
    def dislikePost(self):
        pass



# Record Observaions

    def getPagePosts(self, n=10):
        pass