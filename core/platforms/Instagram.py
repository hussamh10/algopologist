import sys

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

from core.utils.log import *
from core.utils.util import wait; sys.path.append('..')
from core.platforms.Platform import Platform

# https://piprogramming.org/articles/How-to-make-Selenium-undetectable-and-stealth--7-Ways-to-hide-your-Bot-Automation-from-Detection-0000000017.html

import core.constants as constants


class Instagram(Platform):

    name = 'instagram'
    url='https://www.instagram.com'
    search_url='NONE'

    def __init__(self, user):
        super().__init__(Instagram.name, Instagram.url, user)

    def _searchTermUrl(self, term):
        error("No search url for instagram!, use search bar")

    def _searchTermBar(self, term):
        search = self.driver.find_elements(By.XPATH, "//span[text()='Search']")[0]
        search.click()
        wait(1)
        search_bar = self.driver.find_elements(By.XPATH, "//input[@aria-label='Search input']")[0]
        search_bar.send_keys(term)
        wait(1)
    
    def searchTerm(self, term, bar=True):
        return super().searchTerm(term, True)
    
    def getPagePosts(self):
        pass

    def getHomePage(self):
        # sleep(1)
        # home = self.driver.find_element(By.XPATH, '//a[@aria-label="Home"]')
        # home.click()
        pass
    
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

    def likePost(self):
        pass

    def createUser(self):
        pass
