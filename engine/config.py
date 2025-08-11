### CONSTANTS ###
NUM_DAYS = 10

### DIFFICULTY CONFIG ### 
DIFF_CFG = {
    "easy":{
        "starve_morale_every_n_days": 3, 
        "low_food_death_days": 4, 
        "low_morale_death_days": 4,
        "surprise_chance": 0.25, 
        "risk_success_bonus": +0.1
        },
    "normal":{
        "starve_morale_every_n_days": 2, 
        "low_food_death_days": 3, 
        "low_morale_death_days": 3,
        "surprise_chance": 0.20, 
        "risk_success_bonus":  0.00
        },
    "hard":{
        "starve_morale_every_n_days": 1, 
        "low_food_death_days": 2, 
        "low_morale_death_days": 2,
        "surprise_chance": 0.15, 
        "risk_success_bonus": -0.1
        },
}
 ### STARTING VALUES PER DIFFICULTY
STARTS = {
  "easy":   {"hp":6,"food":4,"morale":4,"hp_max":6,"food_max":9,"morale_max":6},
  "normal": {"hp":5,"food":3,"morale":3,"hp_max":5,"food_max":8,"morale_max":5},
  "hard":   {"hp":4,"food":2,"morale":2,"hp_max":4,"food_max":7,"morale_max":4},
}

### SCORE MULTIPLIER ###
DIFF_SCORE_MULT = {
    "easy": 1.0, 
    "normal": 2.0, 
    "hard": 3.0
}