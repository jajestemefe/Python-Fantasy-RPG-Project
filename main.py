from engine import clear_screen, display_intro, Colors, display_stats
from entities import Player
from world import encounter_generator
from combat import combat_loop
import save_manager
import time
import os

def is_skip_intro():
    clear_screen()
    print(f"{Colors.YELLOW}Skip intro? (y/n) > {Colors.RESET}")
    if input().strip() != 'y':
        clear_screen()
        display_intro()
    clear_screen()

def main_menu(player: Player, rooms):
    """The main interactive loop for the game."""
    while True:
        display_stats(player)  # Persistent HUD
        print(f"\n{Colors.CYAN}--- MAIN MENU ---{Colors.RESET}")
        print("[1] Explore the Dungeon")
        print("[2] Check Inventory")
        print("[3] Save Game")
        print("[4] Load Game")
        print("[5] Delete Save")
        print("[6] New Game")
        print("[7] Quit")

        choice = input("What would you like to do? > ").strip()

        if choice == '1':
            clear_screen()
            display_stats(player)
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
            clear_screen()
            display_stats(player)
            # NEW: Interactive Inventory Loop
            while True:
                clear_screen()
                display_stats(player)
                print(f"\n{player.name}'s Inventory:")

                for item, quantity in player.inventory.items():
                    if quantity > 0:  # Only show items we actually have
                        print(f"- {item}: {quantity}")

                inv_choice = input(
                    f"\n{Colors.YELLOW}Type 'use potion' to heal, or press Enter to return > {Colors.RESET}").strip().lower()

                if inv_choice == 'use potion' or inv_choice == 'use health potion':
                    if player.inventory.get("Health Potion", 0) > 0:
                        if player.health == player.max_health:
                            print(f"\n{Colors.YELLOW}You already have full health!{Colors.RESET}")
                        else:
                            player.heal(30)
                            player.inventory["Health Potion"] -= 1
                            print(f"\n{Colors.GREEN}You drank a Health Potion and recovered 30 HP!{Colors.RESET}")
                    else:
                        print(f"\n{Colors.RED}You don't have any Health Potions!{Colors.RESET}")
                    time.sleep(1.5)
                elif inv_choice == '':
                    break  # Back to main menu
                else:
                    print(f"\n{Colors.RED}Invalid command.{Colors.RESET}")
                    time.sleep(1)
            clear_screen()

        elif choice == '3':
            save_slot = input("\nEnter a name for this save slot (e.g., '1', 'my_save') > ").strip()
            if save_slot:
                filepath = os.path.join(save_manager.SAVE_DIR, f"{save_slot}.json")
                if os.path.exists(filepath):
                    confirm = input(
                        f"{Colors.YELLOW}Warning: Save '{save_slot}' already exists. Overwrite? (y/n) > {Colors.RESET}").lower()
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
                for idx, save_file in enumerate(save_files, 1):
                    name = os.path.basename(save_file).replace('.json', '')
                    print(f"[{idx}] {name}")

                save_choice = input("\nEnter the number of the save to load (or press Enter to cancel) > ").strip()

                if save_choice.isdigit() and 1 <= int(save_choice) <= len(save_files):
                    chosen_file = save_files[int(save_choice) - 1]
                    slot_name = str(os.path.basename(chosen_file)).replace('.json', '')

                    loaded_hero = save_manager.load_game(slot_name)
                    if loaded_hero:
                        player = loaded_hero  # Dynamically overwrite current player
                        print(f"{Colors.GREEN}\nWelcome back, {player.name}!{Colors.RESET}")
                elif save_choice:
                    print(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)
            clear_screen()

        elif choice == '5':
            # NEW: Delete Save Logic
            save_files = save_manager.get_save_files()
            if not save_files:
                print(f"{Colors.YELLOW}No save files found to delete.{Colors.RESET}")
            else:
                print("\nAvailable Saves:")
                for idx, save_file in enumerate(save_files, 1):
                    name = os.path.basename(save_file).replace('.json', '')
                    print(f"[{idx}] {name}")

                del_choice = input("\nEnter the number of the save to delete (or press Enter to cancel) > ").strip()

                if del_choice.isdigit() and 1 <= int(del_choice) <= len(save_files):
                    chosen_file = save_files[int(del_choice) - 1]
                    slot_name = str(os.path.basename(chosen_file)).replace('.json', '')

                    confirm = input(
                        f"{Colors.RED}Are you sure you want to delete '{slot_name}'? This cannot be undone. (y/n) > {Colors.RESET}").strip().lower()
                    if confirm == 'y':
                        save_manager.delete_save(slot_name)
                elif del_choice:
                    print(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)
            clear_screen()

        elif choice == '6':
            # NEW: New Game Logic
            confirm = input(
                f"\n{Colors.YELLOW}Start a new game? Any unsaved progress will be lost. (y/n) > {Colors.RESET}").strip().lower()
            if confirm == 'y':
                is_skip_intro()

                player_name = input(f"{Colors.YELLOW}What is your name, adventurer? > {Colors.RESET}").strip()
                if not player_name:
                    player_name = "Nameless Hero"

                # Overwrite current player and generator completely
                player = Player(name=player_name)
                rooms = encounter_generator()
                print(f"\n{Colors.GREEN}New adventure started! Good luck, {player.name}...{Colors.RESET}")
                time.sleep(1.5)
            clear_screen()

        elif choice == '7':
            print("\nThanks for playing! Goodbye.")
            break

        else:
            print(f"\n{Colors.RED}Invalid choice. Please enter a number between 1 and 7.{Colors.RESET}")
            time.sleep(1)
            clear_screen()


def main():
    """The main entry point for the game."""
    clear_screen()

    hero = None
    saves = save_manager.get_save_files()

    if saves:
        load_choice = input(
            f"{Colors.YELLOW}Save files found. Do you want to load a game? (y/n) > {Colors.RESET}").strip().lower()

        if load_choice == 'y':
            while True:
                print("\nAvailable Saves:")
                for idx, save_file in enumerate(saves, 1):
                    name = os.path.basename(save_file).replace('.json', '')
                    print(f"[{idx}] {name}")

                save_choice = input(
                    "\nEnter the number of the save to load (or press Enter to start a new game) > ").strip()

                if save_choice.isdigit() and 1 <= int(save_choice) <= len(saves):
                    chosen_file = saves[int(save_choice) - 1]
                    slot_name = str(os.path.basename(chosen_file)).replace('.json', '')
                    hero = save_manager.load_game(slot_name)

                    if hero:
                        print(f"\n{Colors.GREEN}Welcome back, {hero.name}!{Colors.RESET}")
                        time.sleep(1.5)
                        break
                elif not save_choice:
                    print(f"{Colors.YELLOW}Starting a new game...{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}Invalid selection. Please try again.{Colors.RESET}")

    else:
        is_skip_intro()

    if hero is None:
        player_name = input(f"{Colors.YELLOW}What is your name, adventurer? > {Colors.RESET}").strip()
        if not player_name:
            player_name = "Nameless Hero"
        hero = Player(name=player_name)

    clear_screen()
    dungeon_rooms = encounter_generator()
    print(f"{Colors.GREEN}New adventure started! Good luck, {hero.name}...{Colors.RESET}")
    time.sleep(1.5)
    clear_screen()
    main_menu(hero, dungeon_rooms)


if __name__ == "__main__":
    main()