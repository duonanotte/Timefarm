from shutil import get_terminal_size as gts
from colorama import Fore, Style
from time import sleep

andge_group = f'''
                                                                      
     

████████ ██ ███    ███ ███████ ███████  █████  ██████  ███    ███ 
   ██    ██ ████  ████ ██      ██      ██   ██ ██   ██ ████  ████ 
   ██    ██ ██ ████ ██ █████   █████   ███████ ██████  ██ ████ ██ 
   ██    ██ ██  ██  ██ ██      ██      ██   ██ ██   ██ ██  ██  ██ 
   ██    ██ ██      ██ ███████ ██      ██   ██ ██   ██ ██      ██ 
                                                                  
                                                                                                                                                                                                                                                                                                                                                                                                                                   
'''


def banner():
    '''Вывод баннера'''

    for andge in andge_group.split('\n'):  # Вывод баннера
        print(Fore.CYAN + andge.center(gts()[0], ' ') + Style.RESET_ALL)
        sleep(0.025)