import re
import time
from entities import Player, Enemy
from engine import Colors, clear_screen


# 1. CUSTOM EXCEPTION (2 pts)
class InvalidCombatActionError(Exception):
    """Raised when the player types a command the game doesn't understand."""
    pass


def parse_combat_command(command: str):
    """
    2. REGULAR EXPRESSIONS (1 pt)
    Parses commands like 'attack goblin' or 'use potion' using regex.
    """
    match = re.match(r"(?i)^(attack|use)\s+(.+)$", command.strip())

    if not match:
        raise InvalidCombatActionError(f"I don't understand '{command}'. Try 'attack <target>' or 'use potion'.")

    action = match.group(1).lower()
    target = match.group(2).lower()
    return action, target


def combat_loop(player: Player, enemy: Enemy):
    """The main loop for fighting an enemy."""
    clear_screen()
    print(f"\n--- COMBAT INITIATED: {player.name} vs {enemy.name} ---")

    while player.is_alive() and enemy.is_alive():
        print(f"\n{player.name} HP: {player.health}/{player.max_health}")
        print(f"{enemy.name} HP: {enemy.health}/{enemy.max_health}")

        available_items = {item: qty for item, qty in player.inventory.items() if qty > 0}
        sorted_items = sorted(available_items.items(), key=lambda x: x[0])

        print("Your available items:", ", ".join([f"{k} ({v})" for k, v in sorted_items]))

        print("\nActions:")
        print(f"[1] Attack {enemy.name}")
        print("[2] Use Health Potion")

        raw_command = input("\nWhat will you do? (Choose 1, 2, or type command) > ").strip()

        # The Shortcut Interceptor
        if raw_command == "1":
            command_to_parse = f"attack {enemy.name}"
        elif raw_command == "2":
            command_to_parse = "use potion"
        else:
            command_to_parse = raw_command

        try:
            action, target = parse_combat_command(command_to_parse)

            if action == "attack":
                clear_screen()
                print(f"\nYou attack the {enemy.name} for {player.attack_power} damage!")
                enemy.take_damage(player.attack_power)

            elif action == "use":
                clear_screen()
                if "potion" in target:
                    if player.inventory.get("Health Potion", 0) > 0:
                        player.heal(30)
                        player.inventory["Health Potion"] -= 1
                        print(f"\n{Colors.GREEN}You drank a Health Potion and recovered 30 HP!{Colors.RESET}")
                    else:
                        # NEW EXPLICIT WARNING
                        print(
                            f"\n{Colors.RED}You reach into your bag, but you are out of Health Potions!{Colors.RESET}")
                        continue
                else:
                    print(f"\n{Colors.RED}You can't use that right now!{Colors.RESET}")
                    continue

        except InvalidCombatActionError as e:
            print(f"\n{Colors.RED}[Error] {e}{Colors.RESET}")
            continue

        if enemy.is_alive():
            time.sleep(1)
            print(f"\nThe {enemy.name} attacks you for {enemy.attack_power} damage!")
            player.take_damage(enemy.attack_power)

    if player.is_alive():
        clear_screen()
        player.xp += enemy.xp_reward
        print(f"\n*** You defeated the {enemy.name}! You gained {enemy.xp_reward} XP. ***")
        time.sleep(1.5)
        return True
    else:
        clear_screen()
        print("\n*** You have been defeated... ***")
        time.sleep(1.5)
        return False