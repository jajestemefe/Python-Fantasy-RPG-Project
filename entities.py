import time

import engine
from engine import print_anim, clear_screen


class Character:
    """Base class for all characters in the game."""

    def __init__(self, name: str, health: int, attack_power: int):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack_power = attack_power

    def take_damage(self, amount: int):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def is_alive(self) -> bool:
        return self.health > 0


class Player(Character):
    """The main player character."""

    # ── attack_power is a computed property ──────────────────────────────────
    # base_attack_power  : permanent value (base 10 + weapon bonus + book bonuses)
    # temp_attack_bonus  : cleared after every combat encounter
    # attack_power       : what enemies and combat code actually see

    @property
    def attack_power(self) -> int:
        return self.base_attack_power + self.temp_attack_bonus

    @attack_power.setter
    def attack_power(self, value: int):
        # Allows save_manager (and super().__init__) to set the base directly.
        self.base_attack_power = value

    def __init__(self, name: str):
        # Initialize temp_attack_bonus BEFORE super().__init__ so that the
        # attack_power setter (called by super) doesn't crash.
        self.temp_attack_bonus: int = 0
        self.base_attack_power: int = 0   # will be set to 10 by super().__init__
        super().__init__(name, health=100, attack_power=10)

        self.xp: int = 0
        self.equipped_weapon: str = "Rusty Sword"
        self.read_books: set[str] = set()   # tracks single-use books already read

        self.inventory: dict[str, int] = {
            "Health Potion": 2,
            "Rusty Sword":   1,
        }

    def heal(self, amount: int):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def reset_temp_buffs(self):
        """Strip all temporary combat bonuses. Called automatically after each fight."""
        self.temp_attack_bonus = 0


class Enemy(Character):
    """An adversary encountered in the dungeon."""

    def __init__(self, name: str, health: int, attack_power: int, xp_reward: int):
        super().__init__(name, health, attack_power)
        self.xp_reward = xp_reward


def create_player() -> Player:
    """Prompt for a name and return a fresh Player."""
    clear_screen()
    print_anim(f"{engine.Colors.YELLOW}What is your name, adventurer?")
    player_name = input(f"> {engine.Colors.RESET}").strip()
    if not player_name:
        player_name = "Nameless Hero"

    hero = Player(name=player_name)
    engine.clear_screen()
    engine.print_anim(
        f"{engine.Colors.GREEN}New adventure started! Good luck, {hero.name}...{engine.Colors.RESET}")
    time.sleep(2)
    return hero
