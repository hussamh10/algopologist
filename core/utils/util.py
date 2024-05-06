from core.utils.log import debug
from time import sleep
import random
import re
from tqdm import tqdm

def convertStringToNumber(number):
    num = number.replace(',', '')
    num = num.replace('K', '000')
    num = num.replace('M', '000000')
    num = num.replace('B', '000000000')
    num = re.findall(r'\d+', num)
    if len(num) == 0:
        return 0
    try:
        num = int(''.join(num))
    except:
        num = 0
        raise Warning('Could not convert string to number')
    return num


def wait(sec):
    # sleep for sec but preturb randomly
    sec = sec + random.uniform(0, 1)
    sleep(sec)
    sleep(6)

def waitMinute():
    for i in tqdm(range(60)):
        sleep(1)