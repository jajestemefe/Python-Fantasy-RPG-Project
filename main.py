import re
import time
import os

from engine import clear_screen, Colors, display_stats, print_anim, is_skip_intro
from entities import Player, create_player
from save_manager import ask_if_load
from world import encounter_generator
from combat import combat_loop
from item_manager import get_item, apply_item
import save_manager


# ── Inventory helpers ─────────────────────────────────────────────────────────

def _item_tag(name: str, player: Player) -> str:
    """Return a colored tag if the item is the currently equipped weapon."""
    if name == player.equipped_weapon:
        return f" {Colors.GREEN}[EQUIPPED]{Colors.RESET}"
    return ""


def _show_inventory(player: Player):
    """Render the full inventory with descriptions, types, and equipped status."""
    clear_screen()
    display_stats(player)
    print_anim(f"\n{Colors.CYAN}=== {player.name}'s Inventory ==={Colors.RESET}")
    print_anim(f"Weapon equipped : {player.equipped_weapon}  |  Attack power : {player.attack_power}\n")

    # List comprehension: items the player actually carries
    carried = [(name, qty) for name, qty in sorted(player.inventory.items()) if qty > 0]

    if not carried:
        print_anim("  (your bag is empty)")
        return

    for name, qty in carried:
        item_def = get_item(name)
        tag  = _item_tag(name, player)
        desc = f"  {Colors.CYAN}» {item_def.description}{Colors.RESET}" if item_def else ""
        print(f"  {name} x{qty}{tag}")
        if desc:
            print(desc)

    print_anim(f"\n{Colors.YELLOW}Commands:{Colors.RESET}")
    print_anim("  use <item>    — use a potion or strength potion")
    print_anim("  equip <item>  — equip a weapon")
    print_anim("  read <item>   — read a book")
    print_anim("  Enter         — return to main menu")


def _inventory_loop(player: Player):
    """Interactive inventory screen."""
    while True:
        _show_inventory(player)
        raw = input("\n> ").strip()

        if not raw:
            break

        # Accept 'use', 'equip', or 'read' as verbs — all route to item.use_in_menu().
        match = re.match(r"(?i)^(?:use|equip|read)\s+(.+)$", raw)
        if not match:
            print_anim(f"\n{Colors.RED}Unknown command. Try 'use <item>', 'equip <item>', or 'read <item>'.{Colors.RESET}")
            time.sleep(1.5)
            continue

        target = match.group(1).strip()

        # Case-insensitive search through current inventory (generator expression)
        matched_name = next(
            (n for n in player.inventory if n.lower() == target.lower() and player.inventory[n] > 0),
            None,
        )

        if matched_name is None:
            print_anim(f"\n{Colors.RED}You don't have '{target}' in your bag.{Colors.RESET}")
        else:
            success, msg = apply_item(player, matched_name, "menu")
            color = Colors.GREEN if success else Colors.RED
            print_anim(f"\n{color}{msg}{Colors.RESET}")

        time.sleep(1.8)


# ── Main game menu ────────────────────────────────────────────────────────────

def main_menu(player: Player, rooms):
    """The main interactive loop for the game."""
    while True:
        clear_screen()
        display_stats(player)
        print_anim(f"\n{Colors.CYAN}--- MAIN MENU ---{Colors.RESET}")
        print_anim("[1] Explore the Dungeon")
        print_anim("[2] Check Inventory")
        print_anim("[3] Save Game")
        print_anim("[4] Load Game")
        print_anim("[5] Delete Save")
        print_anim("[6] New Game")
        print_anim("[7] Quit")

        choice = input("\nWhat would you like to do? > ").strip()

        # ── Explore ──────────────────────────────────────────────────────────
        if choice == "1":
            clear_screen()
            display_stats(player)
            print_anim("\nYou step forward into the darkness...")
            time.sleep(1)

            encounter = next(rooms)

            if isinstance(encounter, str):
                if encounter == "empty":
                    print_anim("The room is cold and empty. You move on safely.")
                elif encounter == "trap":
                    damage = 15
                    player.take_damage(damage)
                    print_anim(
                        f"{Colors.RED}SNAP! You stepped on a trap and took {damage} damage!{Colors.RESET}"
                    )
                    print_anim(f"Current HP: {player.health}/{player.max_health}")

            elif isinstance(encounter, dict):
                item  = encounter["item"]
                qty   = encounter["quantity"]
                print_anim(f"{Colors.GREEN}You found a chest: {qty}x {item}!{Colors.RESET}")
                player.inventory[item] = player.inventory.get(item, 0) + qty

            else:
                print_anim(f"A {encounter.name} blocks your path!")
                time.sleep(1)
                survived = combat_loop(player, encounter)
                if not survived:
                    print_anim("\nGame Over. Restart to try again.")
                    break

            input("\nPress Enter to return to the menu...")

        # ── Inventory ────────────────────────────────────────────────────────
        elif choice == "2":
            _inventory_loop(player)

        # ── Save ─────────────────────────────────────────────────────────────
        elif choice == "3":
            save_slot = input("\nEnter a name for this save slot > ").strip()
            if save_slot:
                filepath = os.path.join(save_manager.SAVE_DIR, f"{save_slot}.json")
                if os.path.exists(filepath):
                    confirm = input(
                        f"{Colors.YELLOW}Save '{save_slot}' already exists. Overwrite? (y/n) > {Colors.RESET}"
                    ).lower()
                    if confirm != "y":
                        print_anim(f"{Colors.RED}Save cancelled.{Colors.RESET}")
                        time.sleep(1.5)
                        continue
                save_manager.save_game(player, save_slot)
            else:
                print_anim(f"{Colors.RED}Invalid save name. Cancelled.{Colors.RESET}")
            time.sleep(1.5)

        # ── Load ─────────────────────────────────────────────────────────────
        elif choice == "4":
            save_files = save_manager.get_save_files()
            if not save_files:
                print_anim(f"{Colors.YELLOW}No save files found.{Colors.RESET}")
            else:
                print_anim("\nAvailable saves:")
                for idx, sf in enumerate(save_files, 1):
                    name = os.path.basename(sf).replace(".json", "")
                    print_anim(f"  [{idx}] {name}")

                save_choice = input("\nEnter number to load (or Enter to cancel) > ").strip()
                if save_choice.isdigit() and 1 <= int(save_choice) <= len(save_files):
                    slot_name   = os.path.basename(save_files[int(save_choice) - 1]).replace(".json", "")
                    loaded_hero = save_manager.load_game(slot_name)
                    if loaded_hero:
                        player = loaded_hero
                        print_anim(f"{Colors.GREEN}\nWelcome back, {player.name}!{Colors.RESET}")
                elif save_choice:
                    print_anim(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)

        # ── Delete save ───────────────────────────────────────────────────────
        elif choice == "5":
            save_files = save_manager.get_save_files()
            if not save_files:
                print_anim(f"{Colors.YELLOW}No save files found to delete.{Colors.RESET}")
            else:
                print_anim("\nAvailable saves:")
                for idx, sf in enumerate(save_files, 1):
                    name = os.path.basename(sf).replace(".json", "")
                    print_anim(f"  [{idx}] {name}")

                del_choice = input("\nEnter number to delete (or Enter to cancel) > ").strip()
                if del_choice.isdigit() and 1 <= int(del_choice) <= len(save_files):
                    slot_name = os.path.basename(save_files[int(del_choice) - 1]).replace(".json", "")
                    confirm   = input(
                        f"{Colors.RED}Delete '{slot_name}'? This cannot be undone. (y/n) > {Colors.RESET}"
                    ).strip().lower()
                    if confirm == "y":
                        save_manager.delete_save(slot_name)
                elif del_choice:
                    print_anim(f"{Colors.RED}Invalid selection.{Colors.RESET}")

            time.sleep(1.5)

        # ── New game ──────────────────────────────────────────────────────────
        elif choice == "6":
            confirm = input(
                f"\n{Colors.YELLOW}Start a new game? Unsaved progress will be lost. (y/n) > {Colors.RESET}"
            ).strip().lower()
            if confirm == "y":
                is_skip_intro()
                player = create_player()
                rooms  = encounter_generator()
                time.sleep(1.5)

        # ── Quit ──────────────────────────────────────────────────────────────
        elif choice == "7":
            print_anim("\nThanks for playing! Goodbye.")
            break

        else:
            print_anim(f"\n{Colors.RED}Invalid choice. Enter a number between 1 and 7.{Colors.RESET}")
            time.sleep(1)


# ── Entry point ───────────────────────────────────────────────────────────────

def start():
    """Main entry point. ask_if_load() always returns a valid Player."""
    clear_screen()
    hero          = ask_if_load()          # BUG FIXED: never returns None anymore
    dungeon_rooms = encounter_generator()
    clear_screen()
    main_menu(hero, dungeon_rooms)


if __name__ == "__main__":
    start()
