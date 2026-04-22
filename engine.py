from __future__ import annotations
import sys
import time
import os
from functools import wraps
from typing import TYPE_CHECKING

# Import Player only for static type checking — avoids a circular import at runtime.
if TYPE_CHECKING:
    from entities import Player

# ANSI Color Codes natively supported by WSL
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

def clear_screen():
    """Clears the terminal screen for a clean UI."""
    print("\033[2J\033[H", end="")
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(delay = 0.03, color = Colors.RESET):
    """
    A custom decorator that prints the output of a function
    character by character to simulate a typewriter effect.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            if text:
                sys.stdout.write(color)
                for char in text:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(delay)
                print() # new line
        return wrapper
    return decorator

@typewriter(delay = 0.01, color = Colors.CYAN)
def display_intro():
    return """
        =========================================
              WELCOME TO THE DUNGEONS OF PPY     
        =========================================
        You awaken in a dark, cold room. 
        The smell of damp stone fills the air.
        Your journey begins now...\n
        """
@typewriter(delay = 0.01, color = Colors.CYAN)
def print_anim(s: str):
    return s

def display_stats(player: Player):
    """Draws a persistent HUD at the top of the screen."""
    print(f"{Colors.MAGENTA}===================================================={Colors.RESET}")
    print(
        f"{Colors.MAGENTA} ADVENTURER: {player.name} | HP: {player.health}/{player.max_health} | XP: {player.xp} {Colors.RESET}")
    print(f"{Colors.MAGENTA}===================================================={Colors.RESET}")

def is_skip_intro():
    clear_screen()
    print_anim(f"{Colors.YELLOW}Skip intro? (y/n) > {Colors.RESET}")
    if input().strip() != 'y':
        clear_screen()
        display_intro()
        if input().strip():
            clear_screen()
    clear_screen()