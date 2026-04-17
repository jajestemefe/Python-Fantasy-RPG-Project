from engine import clear_screen, display_intro
from entities import Player
import time

def main_menu(player: Player):
    """The main interactive loop for the game."""
    while True:
        print("\n--- MAIN MENU ---")
        print("[1] Explore the Dungeon")
        print("[2] Check Inventory")
        print("[3] Save Game")
        print("[4] Quit")

        choice = input("What would you like to do? > ")

        if choice == '1':
            print("\nYou step forward into the darkness...")
            time.sleep(1)
            #
        elif choice == '2':
            print(f"\n{player.name}'s Inventory:")
            #
            for item, quantity in player.inventory.items():
                print(f"- {item}: {quantity}")
            input("\Press Enter to continue...")
            clear_screen()
        elif choice == '3':
            print("\Saving game...")
        elif choice == '4':
            print("\nThanks for playing! Goodbye.")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    clear_screen()
    display_intro()

    hero = Player(name = "Hero")
    main_menu(hero)