from colorama import Fore, Back, Style
import inspect
from datetime import datetime

def error(e):
    # get caller funciton name  
    curname = inspect.currentframe()
    calframe = inspect.getouterframes(curname, 2)
    f = calframe[1][3]
    print(Fore.GREEN + f"{f}:" + Fore.RED + f"\t {e}")
    log(f"ERROR: {e}", p=False, caller=inspect.stack())

def info(e):
    curname = inspect.currentframe()
    calframe = inspect.getouterframes(curname, 2)
    f = calframe[1][3]
    print(Fore.GREEN + f"{f}:" + Fore.WHITE + f"\t {e}")
    log(f"INFO: {e}", p=False, caller=inspect.stack())

def debug(e):
    curname = inspect.currentframe()
    calframe = inspect.getouterframes(curname, 2)
    f = calframe[1][3]
    print(Fore.YELLOW + f"{f}:" + Fore.WHITE + f"\t {e}")
    log(f"DEBUG: {e}", p=False, caller=inspect.stack())

def logging(e):
    filename = 'log.txt'
    f = open(filename, 'a')
    debug(e)
    f.write(e)
    f.close()

def log(e, p=False, caller=False):
    from core.experiment.Experiment import Experiment

    try:
        filename = Experiment().log_file()
        f = open(filename, 'a')
        if not caller:
            caller = inspect.stack()

        line = '···'
        for call in caller[::-1]:
            call = f"{call[1].split('/')[-1]} • {call[3]} • {call[2]} • {call[4][0].strip()}"
            line += call + ' ► '
        
        line += f" \n {e} \n"
        f.write(line)
        f.close()
    except:
        pass
    

def pprint(e):
    print(e)