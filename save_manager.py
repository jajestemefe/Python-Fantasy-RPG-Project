import json
import os
import glob
from entities import Player
from engine import Colors

SAVE_DIR = "saves"

# Automatically create the 'saves' directory if it doesn't exist when the game boots
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


def get_save_files():
    """Returns a list of available save files."""
    return glob.glob(os.path.join(SAVE_DIR, "*.json"))


def save_game(player: Player, slot_name: str):
    """Saves the player's state to a specific JSON file."""
    data = {
        "name": player.name,
        "health": player.health,
        "max_health": player.max_health,
        "attack_power": player.attack_power,
        "inventory": player.inventory
    }

    # Save the file directly into the saves/ folder
    filepath = os.path.join(SAVE_DIR, f"{slot_name}.json")
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

    print(f"\n{Colors.GREEN}[ Game successfully saved to slot '{slot_name}'! ]{Colors.RESET}")


def load_game(slot_name: str) -> Player | None:
    """Loads the player's state from a JSON file."""
    filepath = os.path.join(SAVE_DIR, f"{slot_name}.json")
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r") as file:
        data = json.load(file)

    loaded_player = Player(name=data["name"])
    loaded_player.health = data["health"]
    loaded_player.max_health = data["max_health"]
    loaded_player.attack_power = data["attack_power"]
    loaded_player.inventory = data["inventory"]

    return loaded_player