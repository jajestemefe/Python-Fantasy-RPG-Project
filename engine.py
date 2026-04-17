import sys
import time
import os
from functools import wraps

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
        Your journey begins now...
        """