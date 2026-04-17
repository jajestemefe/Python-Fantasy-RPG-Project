import sys
import time
import os
from functools import wraps

def clear_screen():
    """Clears the terminal screen for a clean UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(delay = 0.03):
    """
    A custom decorator that prints the output of a function
    character by character to simulate a typewriter effect.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            if text:
                for char in text:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(delay)
                print() # new line
        return wrapper
    return decorator

@typewriter(delay = 0.01)
def display_intro():
    return """
        =========================================
              WELCOME TO THE DUNGEONS OF PPY     
        =========================================
        You awaken in a dark, cold room. 
        The smell of damp stone fills the air.
        Your journey begins now...
        """