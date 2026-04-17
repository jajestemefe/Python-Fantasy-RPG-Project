import random
from entities import Enemy


def encounter_generator():
    """
    A generator function that continuously yields random encounters.
    Satisfies the 'Generator' requirement.
    """
    event_pool = [
        "empty",
        "empty",
        "trap",
        "loot_potion",
        "enemy_goblin",
        "enemy_skeleton"
    ]

    while True:
        event = random.choice(event_pool)

        if event == "enemy_goblin":
            yield Enemy(name="Furious Goblin", health=30, attack_power=5, xp_reward=10)
        elif event == "enemy_skeleton":
            yield Enemy(name="Rattling Skeleton", health=45, attack_power=8, xp_reward=15)
        elif event == "loot_potion":
            yield {"item": "Health Potion", "quantity": 1}
        elif event == "trap":
            yield "trap"
        else:
            yield "empty"