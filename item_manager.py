from abc import ABC, abstractmethod


# ── Abstract base / "interface" ───────────────────────────────────────────────

class Item(ABC):
    """
    Abstract base class that acts as an interface for every item in the game.
    Subclasses must implement use_in_combat(); use_in_menu() has a sensible default.
    """

    def __init__(self, name: str, description: str, consume_on_use: bool = True):
        self.name = name
        self.description = description
        # If True, the item is removed/decremented from inventory after a successful use.
        self.consume_on_use = consume_on_use

    @abstractmethod
    def use_in_combat(self, player, enemy=None) -> tuple[bool, str]:
        """
        Attempt to use this item during combat.
        Returns (success: bool, feedback_message: str).
        """

    def use_in_menu(self, player) -> tuple[bool, str]:
        """
        Attempt to use this item from the inventory screen.
        Default behavior mirrors use_in_combat; override to differ.
        """
        return self.use_in_combat(player)

    @property
    def usable_in_combat(self) -> bool:
        """Whether this item may be used during a fight."""
        return True

    @property
    def usable_in_menu(self) -> bool:
        """Whether this item may be used from the inventory screen."""
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


# ── Potions ───────────────────────────────────────────────────────────────────

class HealthPotion(Item):
    """Restores a fixed amount of hit points."""

    def __init__(self, name: str, heal_amount: int):
        super().__init__(name, f"Restores {heal_amount} HP.")
        self.heal_amount = heal_amount

    def use_in_combat(self, player, enemy=None) -> tuple[bool, str]:
        if player.health >= player.max_health:
            return False, "You're already at full health!"
        player.heal(self.heal_amount)
        return True, f"You drank a {self.name} and recovered {self.heal_amount} HP!"


class StrengthPotion(Item):
    """Boosts attack power temporarily for the current combat encounter."""

    def __init__(self, bonus: int = 5):
        super().__init__(
            "Strength Potion",
            f"Boosts attack by +{bonus} for the current battle only.",
        )
        self.bonus = bonus

    def use_in_combat(self, player, enemy=None) -> tuple[bool, str]:
        player.temp_attack_bonus += self.bonus
        return True, f"Power surges through you! +{self.bonus} attack for this fight!"

    def use_in_menu(self, player) -> tuple[bool, str]:
        return False, "Save that for the heat of battle — it won't help you standing still."

    @property
    def usable_in_menu(self) -> bool:
        return False


# ── Weapons ───────────────────────────────────────────────────────────────────

class Weapon(Item):
    """Can be equipped from the inventory to permanently change base attack power."""

    def __init__(self, name: str, description: str, attack_bonus: int):
        # Weapons are NOT consumed when equipped; they stay in the inventory.
        super().__init__(name, description, consume_on_use=False)
        self.attack_bonus = attack_bonus

    def use_in_combat(self, player, enemy=None) -> tuple[bool, str]:
        return False, "You can't swap weapons mid-combat!"

    def use_in_menu(self, player) -> tuple[bool, str]:
        if player.equipped_weapon == self.name:
            return False, f"The {self.name} is already in your hand."

        # Remove old weapon's bonus, then apply the new one.
        old_weapon = ITEM_REGISTRY.get(player.equipped_weapon)
        if isinstance(old_weapon, Weapon):
            player.base_attack_power -= old_weapon.attack_bonus

        player.equipped_weapon = self.name
        player.base_attack_power += self.attack_bonus
        return True, f"You grip the {self.name}. Attack power is now {player.attack_power}."

    @property
    def usable_in_combat(self) -> bool:
        return False


# ── Books ─────────────────────────────────────────────────────────────────────

class Book(Item):
    """
    Readable from the inventory screen. May grant XP or a permanent attack bonus.
    Single-use: consumed (crumbles) after reading.
    Cannot be used in combat.
    """

    def __init__(
        self,
        name: str,
        description: str,
        lore: str,
        xp_reward: int = 0,
        attack_bonus: int = 0,
    ):
        super().__init__(name, description, consume_on_use=True)
        self.lore = lore
        self.xp_reward = xp_reward
        self.attack_bonus = attack_bonus

    def use_in_combat(self, player, enemy=None) -> tuple[bool, str]:
        return False, "This is not the time for reading!"

    def use_in_menu(self, player) -> tuple[bool, str]:
        if self.name in player.read_books:
            return False, f"You've already absorbed everything '{self.name}' had to offer."

        lines = [
            f'You open "{self.name}" and read by torchlight...',
            f'  "{self.lore}"',
        ]
        if self.xp_reward:
            player.xp += self.xp_reward
            lines.append(f"Knowledge gained: +{self.xp_reward} XP!")
        if self.attack_bonus:
            player.base_attack_power += self.attack_bonus
            lines.append(f"Your technique sharpens: +{self.attack_bonus} permanent attack!")

        player.read_books.add(self.name)
        lines.append("(The pages turn to ash as you finish the last sentence.)")
        return True, "\n".join(lines)

    @property
    def usable_in_combat(self) -> bool:
        return False


# ── Global item registry ──────────────────────────────────────────────────────

ITEM_REGISTRY: dict[str, Item] = {
    # Potions
    "Health Potion":         HealthPotion("Health Potion",         heal_amount=30),
    "Greater Health Potion": HealthPotion("Greater Health Potion", heal_amount=60),
    "Strength Potion":       StrengthPotion(bonus=5),
    # Weapons
    "Rusty Sword":  Weapon("Rusty Sword",  "A worn blade. Better than bare hands.", attack_bonus=0),
    "Steel Sword":  Weapon("Steel Sword",  "Reliable and sharp. +5 attack.",        attack_bonus=5),
    "War Axe":      Weapon("War Axe",      "Heavy and brutal. +10 attack.",         attack_bonus=10),
    # Books
    "Dungeon Codex": Book(
        "Dungeon Codex",
        "Notes scrawled by a fallen adventurer. +20 XP.",
        lore="Beware the lower levels. The darkness there is alive.",
        xp_reward=20,
    ),
    "Battle Manual": Book(
        "Battle Manual",
        "A worn training manual. +2 permanent attack.",
        lore="Strike with intent, not fury. Every wasted blow is an invitation.",
        attack_bonus=2,
    ),
}


def get_item(name: str) -> "Item | None":
    """Look up an item definition by name. Returns None if unrecognized."""
    return ITEM_REGISTRY.get(name)


def apply_item(player, item_name: str, context: str, enemy=None) -> tuple[bool, str]:
    """
    Central dispatcher: look up the item, call the right use method,
    and handle inventory consumption on success.

    context: "combat" | "menu"
    """
    item = get_item(item_name)
    if item is None:
        return False, f"You don't know how to use '{item_name}'."

    if context == "combat":
        if not item.usable_in_combat:
            return False, f"You can't use the {item_name} right now!"
        success, msg = item.use_in_combat(player, enemy)
    else:
        if not item.usable_in_menu:
            return False, f"You can't use the {item_name} here!"
        success, msg = item.use_in_menu(player)

    if success and item.consume_on_use:
        current = player.inventory.get(item_name, 0)
        if current > 0:
            player.inventory[item_name] -= 1
            if player.inventory[item_name] == 0:
                del player.inventory[item_name]

    return success, msg
