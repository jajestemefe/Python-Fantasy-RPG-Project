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

    def is_alive(self)-> bool:
        return self.health > 0

class Player(Character):
    """The main player character."""
    def __init__(self, name: str):
        super().__init__(name, health = 100, attack_power = 10)

        self.xp = 0

        self.inventory = \
        {
            "Health Potion": 2,
            "Rusty Sword": 1
        }

    def heal(self, amount: int):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

class Enemy(Character):
    """The bad guys."""
    def __init__(self, name: str, health: int, attack_power: int, xp_reward: int):
        super().__init__(name, health, attack_power)
        self.xp_reward = xp_reward