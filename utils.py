### battleships common set of utuility functions ####

import os
from constants import Constants


def clear_screen():
    print("\033c", end="")

def display_welcome_screen():
    print(Constants.BANNER)
    start = input("Press Enter to Start the game or I to read the instructions: ")
    if start.upper() == 'I':
        display_instructions()

def display_instructions():
    clear_screen()
    print(Constants.INSTRUCTIONS)
