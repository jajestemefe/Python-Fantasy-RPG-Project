import json
import os
import glob
import time

from entities import Player, create_player
from engine import Colors, print_anim, is_skip_intro, display_intro

SAVE_DIR = "saves"

"""The settings for the player"""
animation = True

# Automatically create the saves directory on first run.
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def get_save_files() -> list[str]:
    """Return a sorted list of all .json save file paths."""
    return sorted(glob.glob(os.path.join(SAVE_DIR, "*.json")))


def delete_save(slot_name: str):
    """Delete a specific save file by slot name."""
    filepath = os.path.join(SAVE_DIR, f"{slot_name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        print_anim(f"\n{Colors.GREEN}[ Save '{slot_name}' deleted successfully. ]{Colors.RESET}")
    else:
        print_anim(f"\n{Colors.RED}[ Save not found. ]{Colors.RESET}")


def save_game(player: Player, slot_name: str):
    """Persist the player's state to a named JSON save file."""
    data = {
        "name":            player.name,
        "health":          player.health,
        "max_health":      player.max_health,
        "attack_power":    player.base_attack_power,   # save base only (no temp buffs)
        "xp":              player.xp,
        "equipped_weapon": player.equipped_weapon,
        "inventory":       player.inventory,
        "read_books":      list(player.read_books),    # sets aren't JSON-serialisable
    }
    filepath = os.path.join(SAVE_DIR, f"{slot_name}.json")
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

    print_anim(f"\n{Colors.GREEN}[ Game saved to slot '{slot_name}'! ]{Colors.RESET}")


def load_game(slot_name: str) -> "Player | None":
    """Load and return a Player from a named JSON save file, or None if not found."""
    filepath = os.path.join(SAVE_DIR, f"{slot_name}.json")
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r") as file:
        data = json.load(file)

    loaded_player = Player(name=data["name"])
    loaded_player.health          = data["health"]
    loaded_player.max_health      = data["max_health"]
    loaded_player.attack_power    = data["attack_power"]   # uses the setter → sets base
    loaded_player.xp              = data.get("xp", 0)
    loaded_player.equipped_weapon = data.get("equipped_weapon", "Rusty Sword")
    loaded_player.inventory       = data["inventory"]
    # read_books was saved as a list; restore as a set (fallback for old saves)
    loaded_player.read_books      = set(data.get("read_books", []))

    return loaded_player


def ask_if_load() -> Player:
    """
    Show save-file options at startup. Always returns a valid Player — never None.
    """
    saves = get_save_files()

    if not saves:
        # No saves exist at all — skip straight to a new game.
        #is_skip_intro()
        display_intro()
        return create_player()

    print_anim(f"{Colors.YELLOW}Save files found. Load a game? (y/n)")
    load_choice = input(f"> {Colors.RESET}").strip().lower()

    if load_choice != "y":
        is_skip_intro()
        return create_player()

    # User wants to load — let them pick a slot.
    while True:
        print_anim("\nAvailable saves:")
        for idx, save_file in enumerate(saves, 1):
            name = os.path.basename(save_file).replace(".json", "")
            print_anim(f"  [{idx}] {name}")

        print_anim("\nEnter number to load (or Enter to start a new game)\n> ")
        save_choice = input().strip()

        if not save_choice:
            print_anim(f"{Colors.YELLOW}Starting a new game...{Colors.RESET}")
            return create_player()

        if save_choice.isdigit() and 1 <= int(save_choice) <= len(saves):
            chosen_file = saves[int(save_choice) - 1]
            slot_name   = os.path.basename(chosen_file).replace(".json", "")
            hero        = load_game(slot_name)
            if hero:
                print_anim(f"\n{Colors.GREEN}Welcome back, {hero.name}!{Colors.RESET}")
                time.sleep(1.5)
                return hero

        print_anim(f"{Colors.RED}Invalid selection. Please try again.{Colors.RESET}")
