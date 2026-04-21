import random
from entities import Enemy


def encounter_generator():
    """
    GENERATOR — continuously yields random dungeon encounters.
    Each call to next() produces a fresh event.
    """
    event_pool = [
        "empty",
        "empty",
        "trap",
        "loot_health_potion",
        "loot_health_potion",
        "loot_greater_potion",
        "loot_strength_potion",
        "loot_steel_sword",
        "loot_war_axe",
        "loot_dungeon_codex",
        "loot_battle_manual",
        "enemy_goblin",
        "enemy_goblin",
        "enemy_skeleton",
        "enemy_troll",
    ]

    while True:
        event = random.choice(event_pool)

        if event == "enemy_goblin":
            yield Enemy(name="Furious Goblin",    health=30, attack_power=5,  xp_reward=10)
        elif event == "enemy_skeleton":
            yield Enemy(name="Rattling Skeleton", health=45, attack_power=8,  xp_reward=15)
        elif event == "enemy_troll":
            yield Enemy(name="Cave Troll",        health=70, attack_power=12, xp_reward=25)
        elif event == "loot_health_potion":
            yield {"item": "Health Potion",         "quantity": 1}
        elif event == "loot_greater_potion":
            yield {"item": "Greater Health Potion", "quantity": 1}
        elif event == "loot_strength_potion":
            yield {"item": "Strength Potion",       "quantity": 1}
        elif event == "loot_steel_sword":
            yield {"item": "Steel Sword",           "quantity": 1}
        elif event == "loot_war_axe":
            yield {"item": "War Axe",               "quantity": 1}
        elif event == "loot_dungeon_codex":
            yield {"item": "Dungeon Codex",         "quantity": 1}
        elif event == "loot_battle_manual":
            yield {"item": "Battle Manual",         "quantity": 1}
        elif event == "trap":
            yield "trap"
        else:
            yield "empty"
