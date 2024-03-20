from datetime import datetime
import sys
sys.path.append('..')

from time import sleep
from core.constants import USERS_PATH
from core.utils.log import pprint, error;
# from browser.Selenium import Browser
from core.browser.Selenium import Browser
import os
import constants
import pickle as pkl
from core.utils.log import debug, info, error
from core.utils.util import wait
import core.utils.monkey as monkey
import pandas as pd


class Google():
    def __init__(self):
        self.url = 'https://accounts.google.com/signin'
        self.users = dict()
    
    def createUsers(self):
        for user in self.users:
            self.createUser(user)

    def loadBrowser(self):
        session = f'google_create'
        print(session)
        browser = Browser(session)
        self.driver = browser.getDriver()
        debug('Browser loaded')
        return self.driver

    def loadWebsite(self):
        self.driver.get(self.url)

    def createUser(self, user):
        email = user
        password = self.users[email]['password']
        firstname = self.users[email]['firstname']
        lastname = self.users[email]['lastname']

        self.loadBrowser()       
        wait(4)
        self.loadWebsite()
        wait(2)

        monkey.next()
        monkey.type(email)
        monkey.enter()
        input()