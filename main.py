from engine import clear_screen, display_intro
from entities import Player
from world import encounter_generator
from combat import combat_loop
import save_manager
import time

def main_menu(player: Player, rooms):
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
            encounter = next(rooms)

            if isinstance(encounter, str):
                if encounter == "empty":
                    print("The room is cold and empty. You move on safely.")

            elif encounter == "trap":
                damage = 15
                player.take_damage(damage)
                print(f"SNAP! You stepped on a trap and took {damage} damage!")
                print(f"Current Health: {player.health}/{player.max_health}")

            elif isinstance(encounter, dict):
                # Comprehensions or basic dictionary logic for loot
                item = encounter["item"]
                qty = encounter["quantity"]
                print(f"You found a chest containing: {qty}x {item}!")
                # Add to inventory safely
                player.inventory[item] = player.inventory.get(item, 0) + qty

            else:
                # It must be an Enemy object!
                print(f"A {encounter.name} blocks your path!")
                time.sleep(1)

                # Launch the combat loop!
                survived = combat_loop(player, encounter)

                if not survived:
                    print("\nGame Over. Restart to try again.")
                    break  # Ends the game loop

            input("\nPress Enter to return to the menu...")
            clear_screen()

        elif choice == '2':
            print(f"\n{player.name}'s Inventory:")
            #
            for item, quantity in player.inventory.items():
                print(f"- {item}: {quantity}")
            input("Press Enter to continue...")
            clear_screen()
        elif choice == '3':
            print("Saving game...")
            save_manager.save_game(player)
            time.sleep(1.5)
            clear_screen()
        elif choice == '4':
            print("\nThanks for playing! Goodbye.")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    clear_screen()
    display_intro()

    hero = None

    # Check if a save file exists and ask to load it
    import os

    if os.path.exists(save_manager.SAVE_FILE):
        load_choice = input("\nA save file was found. Do you want to load it? (y/n) > ").strip().lower()
        if load_choice == 'y':
            hero = save_manager.load_game()
            print(f"\nWelcome back, {hero.name}!")
            time.sleep(1.5)

    # If they didn't load a game, create a new character
    if hero is None:
        player_name = input("\nWhat is your name, adventurer? > ").strip()
        if not player_name:
            player_name = "Nameless Hero"
        hero = Player(name=player_name)

    dungeon_rooms = encounter_generator()
    main_menu(hero, dungeon_rooms)