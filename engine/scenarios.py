import random

### LIST OF CHOICE SCENARIOS ###
scenarios = [
    {
        "description": "You find a dark cave. It might have treasure, or danger.",
        "left_choice": {
            "text": "Explore the cave",
            "chance": 0.5,
            "success_effects": {"hp": 0, "food": 2, "morale": 1},
            "failure_effects": {"hp": -2, "food": 0, "morale": -1},
            "log_text": "You brave the cave."
        },
        "right_choice": {
            "text": "Avoid the cave",
            "effects": {"hp": 0, "food": 0, "morale": 0},
            "log_text": "You played it safe and walked away."
        }
    },
    {
        "description": "A traveling merchant offers a rare herb that boosts morale.",
        "left_choice": {
            "text": "Trade 1 food for the herb",
            "effects": {"hp": 0, "food": -1, "morale": 2},
            "log_text": "You traded food for the herb."
        },
        "right_choice": {
            "text": "Refuse the trade",
            "effects": {"hp": 0, "food": 0, "morale": -1},
            "log_text": "You refused and felt a bit regretful."
        }
    },
    {
        "description": "A wounded knight begs for help by the roadside.",
        "left_choice": {
            "text": "Help the knight",
            "chance": 0.6,
            "success_effects": {"hp": 1, "food": -1, "morale": 2},
            "failure_effects": {"hp": -1, "food": -1, "morale": 0},
            "log_text": "You offered aid to the knight."
        },
        "right_choice": {
            "text": "Ignore the knight",
            "effects": {"hp": 0, "food": 0, "morale": -1},
            "log_text": "You left the knight to their fate."
        }
    },
    {
        "description": "You hear singing in the forest. A fae voice calls your name.",
        "left_choice": {
            "text": "Follow the voice",
            "chance": 0.4,
            "success_effects": {"hp": 0, "food": 1, "morale": 3},
            "failure_effects": {"hp": -2, "food": 0, "morale": -2},
            "log_text": "You venture toward the voice."
        },
        "right_choice": {
            "text": "Stay on your path",
            "effects": {"hp": 0, "food": 0, "morale": 1},
            "log_text": "You resist the temptation and move on."
        }
    },
    {
        "description": "A suspicious goblin offers a 'lucky' rock in exchange for food.",
        "left_choice": {
            "text": "Trade 1 food for the rock",
            "chance": 0.5, 
            "success_effects": {"hp": 0, "food": -1, "morale": 2},
            "failure_effects": {"hp": -1, "food": -1, "morale": -1},
            "log_text": "You give the goblin some food."
        },
        "right_choice": {
            "text": "Chase the goblin away",
            "effects": {"hp": 0, "food": 0, "morale": 1},
            "log_text": "The goblin flees into the woods."
        }
    },
    {
        "description": "A hidden chest is half-buried in the forest floor.",
        "left_choice": {
            "text": "Open the chest",
            "chance": 0.5,
            "success_effects": {"hp": 0, "food": 2, "morale": 2},
            "failure_effects": {"hp": -2, "food": 0, "morale": -1},
            "log_text": "You open the mysterious chest."
        },
        "right_choice": {
            "text": "Leave it alone",
            "effects": {"hp": 0, "food": 0, "morale": 0},
            "log_text": "You leave the chest untouched."
        }
    },
    {
        "description": "You find a sparkling pond said to heal those who drink from it.",
        "left_choice": {
            "text": "Drink from the pond",
            "chance": 0.66,
            "success_effects": {"hp": 2, "food": 0, "morale": 1},
            "failure_effects": {"hp": -2, "food": 0, "morale": -1},
            "log_text": "You drink the mysterious water."
        },
        "right_choice": {
            "text": "Avoid it, fearing a curse",
            "effects": {"hp": 0, "food": 0, "morale": -1},
            "log_text": "You walk past, uneasy but safe."
        }
    },
    {
        "description": "You reach an abandoned watchtower with a rickety ladder.",
        "left_choice": {
            "text": "Climb the tower",
            "chance": 0.5,
            "success_effects": {"hp": 0, "food": 2, "morale": 2},
            "failure_effects": {"hp": -2, "food": 0, "morale": -2},
            "log_text": "You climb the fragile ladder."
        },
        "right_choice": {
            "text": "Ignore the tower",
            "effects": {"hp": 0, "food": 0, "morale": 0},
            "log_text": "You decide it’s too risky to climb."
        }
    },
    {
        "description": "A group of peasants invite you to share their meal.",
        "left_choice": {
            "text": "Accept their invitation",
            "effects": {"hp": 1, "food": 2, "morale": 1},
            "log_text": "You enjoy a warm meal with them."
        },
        "right_choice": {
            "text": "Decline politely",
            "effects": {"hp": 0, "food": 0, "morale": -1},
            "log_text": "You thank them and continue your journey."
        }
    },
    {
        "description": "A howling wolf blocks the forest path.",
        "left_choice": {
            "text": "Try to scare it away",
            "chance": 0.5,
            "success_effects": {"hp": 0, "food": 0, "morale": 1},
            "failure_effects": {"hp": -2, "food": 0, "morale": -1},
            "log_text": "You confront the wolf cautiously."
        },
        "right_choice": {
            "text": "Take a longer detour",
            "effects": {"hp": -1, "food": 0, "morale": -1},
            "log_text": "You take a tiring detour around the wolf."
        }
    }
]

### LIST OF SURPRISE EVENTS ###
def get_random_event(chance=0.2):
    if random.random() < chance:
        return random.choice([
            {"hp": -1, "food": 0, "morale": 0, "text": "A mischievous pixie steals a bite of your rations! -1 HP from the chase"},
            {"hp": 0, "food": 1, "morale": 0, "text": "You stumble upon a glowing mushroom patch! +1 Food"},
            {"hp": 0, "food": 0, "morale": 1, "text": "A group of fireflies dance around you. Your heart feels lighter! +1 Morale"},
            {"hp": -2, "food": 0, "morale": -1, "text": "A sudden landslide forces you to jump aside! -2 HP and morale drops"},
            {"hp": 1, "food": 0, "morale": 1, "text": "A wandering druid blesses you with vitality! +1 HP and +1 Morale"},
            {"hp": 0, "food": 2, "morale": 0, "text": "You find an abandoned picnic basket under a tree! +2 Food"},
            {"hp": -1, "food": 0, "morale": 1, "text": "A cheeky fairy plays a prank, but you laugh it off. -1 HP, +1 Morale"},
            {"hp": 0, "food": -1, "morale": -1, "text": "Rats sneak into your pack during the night! -1 Food and -1 Morale"},
            {"hp": 2, "food": 0, "morale": 0, "text": "A healing spring bubbles nearby. You bathe and feel renewed! +2 HP"},
            {"hp": 0, "food": 0, "morale": 2, "text": "A bard passes by and plays a joyful tune. +2 Morale!"}
        ])
    return -1