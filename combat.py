import re
import time
from entities import Player, Enemy


# 1. CUSTOM EXCEPTION (2 pts)
class InvalidCombatActionError(Exception):
    """Raised when the player types a command the game doesn't understand."""
    pass


def parse_combat_command(command: str):
    """
    2. REGULAR EXPRESSIONS (1 pt)
    Parses commands like 'attack goblin' or 'use potion' using regex.
    """
    # This regex looks for the word 'attack' or 'use', followed by a space, and then the target
    match = re.match(r"(?i)^(attack|use)\s+(.+)$", command.strip())

    if not match:
        # Raising our custom exception!
        raise InvalidCombatActionError(f"I don't understand '{command}'. Try 'attack <target>' or 'use potion'.")

    action = match.group(1).lower()
    target = match.group(2).lower()
    return action, target


def combat_loop(player: Player, enemy: Enemy):
    """The main loop for fighting an enemy."""
    print(f"\n--- COMBAT INITIATED: {player.name} vs {enemy.name} ---")

    while player.is_alive() and enemy.is_alive():
        print(f"\n{player.name} HP: {player.health}/{player.max_health}")
        print(f"{enemy.name} HP: {enemy.health}/{enemy.max_health}")

        # 3. DICTIONARY COMPREHENSION (2 pts)
        # We create a new dictionary containing ONLY items we actually have in stock
        available_items = {item: qty for item, qty in player.inventory.items() if qty > 0}

        # 4. LAMBDA FUNCTION (3 pts)
        # We sort the available items alphabetically by their name (the first element in the tuple 'x[0]')
        sorted_items = sorted(available_items.items(), key=lambda x: x[0])

        print("Your available items:", ", ".join([f"{k} ({v})" for k, v in sorted_items]))

        command = input("\nWhat will you do? (e.g., 'attack enemy', 'use potion') > ")

        try:
            action, target = parse_combat_command(command)

            if action == "attack":
                print(f"\nYou attack the {enemy.name} for {player.attack_power} damage!")
                enemy.take_damage(player.attack_power)

            elif action == "use":
                if "potion" in target and player.inventory.get("Health Potion", 0) > 0:
                    player.heal(30)
                    player.inventory["Health Potion"] -= 1
                    print("\nYou drank a Health Potion and recovered 30 HP!")
                else:
                    print("\nYou don't have that item or can't use it right now!")
                    continue

        except InvalidCombatActionError as e:
            # Catching and handling our custom exception!
            print(f"\n[Error] {e}")
            continue

        # Enemy's turn to attack (if they survived!)
        if enemy.is_alive():
            time.sleep(1)
            print(f"\nThe {enemy.name} attacks you for {enemy.attack_power} damage!")
            player.take_damage(enemy.attack_power)

    # Combat Resolution
    if player.is_alive():
        print(f"\n*** You defeated the {enemy.name}! You gained {enemy.xp_reward} XP. ***")
        time.sleep(1.5)
        return True
    else:
        print("\n*** You have been defeated... ***")
        time.sleep(1.5)
        return False