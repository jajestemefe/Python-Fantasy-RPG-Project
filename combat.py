import re
import time
from entities import Player, Enemy
from engine import Colors, clear_screen, display_stats
from item_manager import get_item, apply_item


# ── Custom exception ──────────────────────────────────────────────────────────

class InvalidCombatActionError(Exception):
    """Raised when the player types a command the game doesn't understand."""
    pass


# ── Command parser ────────────────────────────────────────────────────────────

def parse_combat_command(command: str) -> tuple[str, str]:
    """
    REGULAR EXPRESSIONS — parses commands like 'attack goblin' or 'use potion'.
    Raises InvalidCombatActionError if the input doesn't match the expected pattern.
    """
    match = re.match(r"(?i)^(attack|use)\s+(.+)$", command.strip())
    if not match:
        raise InvalidCombatActionError(
            f"I don't understand '{command}'. Try 'attack <target>' or 'use <item>'."
        )
    return match.group(1).lower(), match.group(2).lower()


# ── Main combat loop ──────────────────────────────────────────────────────────

def combat_loop(player: Player, enemy: Enemy) -> bool:
    """
    Run a turn-based fight between player and enemy.
    Returns True if the player survived, False if defeated.
    """
    clear_screen()
    display_stats(player)
    print(f"\n--- COMBAT INITIATED: {player.name} vs {enemy.name} ---")

    while player.is_alive() and enemy.is_alive():
        print(f"\n{player.name} HP: {player.health}/{player.max_health}")
        print(f"{enemy.name} HP: {enemy.health}/{enemy.max_health}")

        # Only show items that can actually be used in combat (dict comprehension).
        combat_items = {
            name: qty for name, qty in player.inventory.items()
            if qty > 0 and get_item(name) is not None and get_item(name).usable_in_combat
        }
        sorted_combat_items = sorted(combat_items.items(), key=lambda x: x[0])
        item_display = ", ".join(f"{k} ({v})" for k, v in sorted_combat_items) or "none"
        print(f"Usable items: {item_display}")

        print("\nActions:")
        print(f"  [1] Attack {enemy.name}")
        print(f"  [2] Use Health Potion")
        if combat_items:
            print(f"  Or type: use <item name>")

        raw_command = input("\nWhat will you do? > ").strip()

        # Shortcut interceptor
        if raw_command == "1":
            command_to_parse = f"attack {enemy.name}"
        elif raw_command == "2":
            command_to_parse = "use health potion"
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
                # Match target to an actual item in the player's inventory
                # (generator expression — case-insensitive search)
                matched_name = next(
                    (n for n in player.inventory
                     if n.lower() == target and player.inventory[n] > 0),
                    None,
                )
                if matched_name is None:
                    print(f"\n{Colors.RED}You don't have '{target}'.{Colors.RESET}")
                    continue

                success, msg = apply_item(player, matched_name, "combat", enemy)
                color = Colors.GREEN if success else Colors.RED
                print(f"\n{color}{msg}{Colors.RESET}")
                if not success:
                    continue  # Failed uses don't trigger an enemy counter-attack

        except InvalidCombatActionError as e:
            print(f"\n{Colors.RED}[Error] {e}{Colors.RESET}")
            continue

        # Enemy counter-attack (only after a valid player action)
        if enemy.is_alive():
            time.sleep(1)
            print(f"\nThe {enemy.name} attacks you for {enemy.attack_power} damage!")
            player.take_damage(enemy.attack_power)

    # ── Combat end ────────────────────────────────────────────────────────────
    # Always clear temporary buffs regardless of outcome.
    player.reset_temp_buffs()

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
