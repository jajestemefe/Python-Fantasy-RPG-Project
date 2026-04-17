import json
import os
from entities import Player

SAVE_FILE = "savegame.json"


def save_game(player: Player):
    """Saves the player's state to a JSON file. Satisfies serialization requirement."""
    data = {
        "name": player.name,
        "health": player.health,
        "max_health": player.max_health,
        "attack_power": player.attack_power,
        "inventory": player.inventory
    }

    # Using the 'with' context manager to safely open and close the file
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    print("\n[ Game successfully saved! ]")


def load_game() -> Player | None:
    """Loads the player's state from a JSON file if it exists."""
    if not os.path.exists(SAVE_FILE):
        return None

    # Safely open the file using 'with'
    with open(SAVE_FILE, "r") as file:
        data = json.load(file)

    # Recreate the player object with the saved data
    loaded_player = Player(name=data["name"])
    loaded_player.health = data["health"]
    loaded_player.max_health = data["max_health"]
    loaded_player.attack_power = data["attack_power"]
    loaded_player.inventory = data["inventory"]

    return loaded_player