from re import I
from secrets import randbits
import pyautogui as gui
from time import sleep
from random import randint

from core.utils.log import error

gui.FAILSAFE = False

def pause(k=1000):
    t = randint(1, 100)/k
    sleep(t)

def remindMeLater():
    gui.moveTo(950, 185)
    pause()
    gui.click()

def GotIt():
    gui.moveTo(1140, 726)
    pause()
    gui.click()

def click(x=200, y=200):
    gui.moveTo(x, y)
    pause()
    gui.click()

def scroll(N=-100):
    gui.scroll(N)

def enter():
    gui.press('return')
    pause()

def space():
    gui.press('space')
    pause()

def nextPressed():
    gui.press('tab')

def next():
    gui.press('tab')
    pause()

def back():
    gui.hotkey('shift', 'tab')
    pause()

def arrow_down():
    gui.press('down')
    pause()

def right():
    gui.press('right')
    pause()

def arrow_up():
    gui.press('up')
    pause()

def save():
    gui.hotkey('cmd', 's')
    pause()

def press(key):
    gui.press(key)
    pause()

def email():
    error('OTP detected: Please verify the email manually -- press enter to continue')
    input()

def captcha():
    error('Captcha detected: Please solve the captcha manually -- press enter to continue')
    input()

def type(text):
    for char in text:
        gui.press(char)
        pause()

def moveTo(x, y):
    gui.moveTo(x, y)
    pause()