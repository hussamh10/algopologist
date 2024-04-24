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

import core.constants as constants

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
    
    def _searchTermUrl(self, term):
        pass

    # TODO - Implement this
    def convertToObject(self, post, origin):
        obj = {
            'id': post.get('id'),
            'platform': "tiktok",
            'origin': origin,
            'position': post['position'],
            'type': 'post',
            'source': post.get('source'),
            'secondary_source': post.get('secondary_source'),
            # 'likes': post.get('likes'),
            # 'comments': post.get('comments'),
            # 'shares': None,
            # 'views': None,
            # 'created_at': None,
            # 'title': None,
            # 'description': post['selftext'],
            # 'media': None,
            # 'url': post['url'],
            # 'is_ad': None
        }
        return obj

    def chromeLogin(self):
        self.loadPage(TikTok.signin_url)
        sleep(5)

        main_window = self.driver.current_window_handle
        driver = self.driver
        btn = driver.find_element(By.XPATH, "//div[contains(text(), 'Continue with Google')]")
        sleep(4)
        btn.click()
        sleep(2)
        handle = driver.window_handles

        main_window = driver.current_window_handle

        # Switch to new window
        windows = driver.window_handles
        print(windows)
        for window in windows:
            if window != main_window:
                driver.switch_to.window(window)

        btn = driver.find_element(By.XPATH, "//div[contains(@data-identifier, 'spartaaceap.com')]")
        btn.click()
        sleep(2)
        btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Continue')]")
        btn.click()
        sleep(2)
        driver.switch_to.window(main_window)       

    def followUser(self):
        #TODO add user followed.
        tab = self.driver.find_element(By.ID, "tabs-0-tab-search_account")
        tab.click()
        sleep(5)
        # data-e2e="search-user-container"
        users = self.driver.find_elements(By.XPATH, '//*[@data-e2e="search-user-container"]')
        user = users[0]
        user.click()
        sleep(5)
        follow = self.driver.find_element(By.XPATH, '//*[@data-e2e="follow-button"]')
        follow.click()
        sleep(5)

    def openPost(self):
        tab = self.driver.find_element(By.ID, "tabs-0-tab-search_video")
        tab.click()
        sleep(4)
        results = self.driver.find_element(By.XPATH, '//*[@data-e2e="search_video-item-list"]')
        result = results.find_elements(By.TAG_NAME, 'div')[0]
        caption = result.find_element(By.XPATH, '//*[@data-e2e="search-card-video-caption"]').get_attribute('innerText')
        userlink = result.find_element(By.XPATH, '//*[@data-e2e="search-card-user-link"]').get_attribute('href')
        name = result.find_element(By.XPATH, '//*[@data-e2e="search-card-user-unique-id"]').text
        result.click()
        sleep(10)
        sleep(4)
        post = {
            'caption': caption,
            'userlink': userlink,
            'name': name
        }
        self.getHomePage()
        return post

    def likePost(self):
        tab = self.driver.find_element(By.ID, "tabs-0-tab-search_video")
        tab.click()
        sleep(4)
        results = self.driver.find_element(By.XPATH, '//*[@data-e2e="search_video-item-list"]')
        result = results.find_elements(By.TAG_NAME, 'div')[0]
        caption = result.find_element(By.XPATH, '//*[@data-e2e="search-card-video-caption"]').get_attribute('innerText')
        userlink = result.find_element(By.XPATH, '//*[@data-e2e="search-card-user-link"]').get_attribute('href')
        name = result.find_element(By.XPATH, '//*[@data-e2e="search-card-user-unique-id"]').text
        result.click()
        sleep(10)
        self.driver.find_element(By.TAG_NAME, 'body').send_keys('l')
        sleep(4)
        post = {
            'caption': caption,
            'userlink': userlink,
            'name': name
        }
        self.getHomePage()
        return post

# Navigate Platform   
    def createUser(self):
        pass

    def getHomePage(self):
        self.driver.get("https://www.tiktok.com/en/")
        pass

    def loggedIn(self):
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