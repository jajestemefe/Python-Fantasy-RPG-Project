from engine import clear_screen, display_intro, Colors
from entities import Player
from world import encounter_generator
from combat import combat_loop
import save_manager
import time
import os


def main_menu(player: Player, rooms):
    """The main interactive loop for the game."""
    while True:
        print(f"\n{Colors.CYAN}--- MAIN MENU ---{Colors.RESET}")
        print("[1] Explore the Dungeon")
        print("[2] Check Inventory")
        print("[3] Save Game")
        print("[4] Load Game")
        print("[5] Quit")

        choice = input("What would you like to do? > ").strip()

        if choice == '1':
            print("\nYou step forward into the darkness...")
            time.sleep(1)

            encounter = next(rooms)

            if isinstance(encounter, str):
                if encounter == "empty":
                    print("The room is cold and empty. You move on safely.")
                elif encounter == "trap":
                    damage = 15
                    player.take_damage(damage)
                    print(f"{Colors.RED}SNAP! You stepped on a trap and took {damage} damage!{Colors.RESET}")
                    print(f"Current Health: {player.health}/{player.max_health}")

            elif isinstance(encounter, dict):
                item = encounter["item"]
                qty = encounter["quantity"]
                print(f"{Colors.GREEN}You found a chest containing: {qty}x {item}!{Colors.RESET}")
                player.inventory[item] = player.inventory.get(item, 0) + qty

            else:
                print(f"A {encounter.name} blocks your path!")
                time.sleep(1)

                survived = combat_loop(player, encounter)
                if not survived:
                    print("\nGame Over. Restart to try again.")
                    break

            input("\nPress Enter to return to the menu...")
            clear_screen()

        elif choice == '2':
            print(f"\n{player.name}'s Inventory:")
            for item, quantity in player.inventory.items():
                print(f"- {item}: {quantity}")
            input("\nPress Enter to continue...")
            clear_screen()

        elif choice == '3':
            save_slot = input("\nEnter a name for this save slot (e.g., '1', 'my_save') > ").strip()
            if save_slot:
                #OVERWRITE WARNING LOGIC
                filepath = os.path.join(save_manager.SAVE_DIR, f"{save_slot}.json")
                if os.path.exists(filepath):
                    confirm = input(f"{Colors.YELLOW}Warning: Save '{save_slot}' already exists. Overwrite? (y/n) > {Colors.RESET}").lower()
                    if confirm != 'y':
                        print(f"{Colors.RED}Save cancelled.{Colors.RESET}")
                        time.sleep(1.5)
                        clear_screen()
                        continue

                save_manager.save_game(player, save_slot)
            else:
                print(f"{Colors.RED}Invalid save name. Cancelled.{Colors.RESET}")
            time.sleep(1.5)
            clear_screen()

        elif choice == '4':
            save_files = save_manager.get_save_files()
            if not save_files:
                print(f"{Colors.YELLOW}No save files found.{Colors.RESET}")
            else:
                print("\nAvailable Saves:")
                # INDEXED LOAD LIST
                for idx, save_file in enumerate(save_files, 1):
                    name = os.path.basename(save_file).replace('.json', '')
                    print(f"[{idx}] {name}")

                save_choice = input("\nEnter the number of the save to load (or press Enter to cancel) > ").strip()

                # Check if the user typed a valid number
                if save_choice.isdigit() and 1 <= int(save_choice) <= len(save_files):
                    # Match the number back to the correct file
                    chosen_file = save_files[int(save_choice) - 1]
                    slot_name = str(os.path.basename(chosen_file)).replace('.json', '')

                    loaded_hero = save_manager.load_game(slot_name)
                    if loaded_hero:
                        player = loaded_hero
                        print(f"{Colors.GREEN}\nWelcome back, {player.name}!{Colors.RESET}")
                elif save_choice:
                    print(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)
            clear_screen()


        elif choice == '5':
            print("\nThanks for playing! Goodbye.")
            break

        else:
            print(f"\n{Colors.RED}Invalid choice. Please enter a number between 1 and 5.{Colors.RESET}")


if __name__ == "__main__":
    clear_screen()
    display_intro()

    hero = None
    saves = save_manager.get_save_files()

    # Startup check for saves
    if saves:
        load_choice = input(
            f"\n{Colors.YELLOW}Save files found. Do you want to load a game? (y/n) > {Colors.RESET}").strip().lower()
        if load_choice == 'y':
            print("\nAvailable Saves:")
            for s in saves:
                print(f"- {os.path.basename(s).replace('.json', '')}")

            slot = input("\nEnter the name of the save to load > ").strip()
            hero = save_manager.load_game(slot)
            if hero:
                print(f"\n{Colors.GREEN}Welcome back, {hero.name}!{Colors.RESET}")
                time.sleep(1.5)
            else:
                print(f"{Colors.RED}Failed to load. Starting new game.{Colors.RESET}")
                hero = None

    # If they didn't load, make a new character
    if hero is None:
        player_name = input("\nWhat is your name, adventurer? > ").strip()
        if not player_name:
            player_name = "Nameless Hero"
        hero = Player(name=player_name)

    dungeon_rooms = encounter_generator()
    main_menu(hero, dungeon_rooms)