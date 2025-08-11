import engine.utils as utl

### PLAYER CLASS ###
class Player:

    # Initial player stats 
    def __init__(self, hp=5, food=3, morale=3, hp_max=5, food_max=8, morale_max=5, difficulty="normal"):
        self.hp = hp
        self.food = food
        self.morale = morale
        self.difficulty = difficulty

        self.hp_max = hp_max
        self.food_max = food_max
        self.morale_max = morale_max

        self.low_food = 0
        self.low_morale = 0
        self.cause_of_death = "None"

    # Update stats
    def apply_effects(self, hp=0, food=0, morale=0):
        self.update_hp(hp)
        self.update_food(food)
        self.update_morale(morale)

    def update_hp(self, value):
        self.hp = utl.clamp(self.hp + value, 0, self.hp_max)

    def update_food(self, value):
        self.food = utl.clamp(self.food + value, 0, self.food_max)

    def update_morale(self, value):
        self.morale = utl.clamp(self.morale + value, 0, self.morale_max)

    # Check if player is alive
    def is_alive(self):
        return self.hp > 0
    
    # Check for player food and morale + daily decay
    def daily_decay(self, cfg_day_cap):
        self.update_food(-1)

        if self.food <= 0:
            self.low_food += 1
            self.update_hp(-1)
            if self.low_food % cfg_day_cap["starve_morale_every_n_days"] == 0:
                self.update_morale(-1)
        else:
            self.low_food = 0

        if self.morale <= 0:
            self.low_morale += 1
        else:
            self.low_morale = 0

    def is_food_low(self, food_days):
        return self.low_food >= food_days
    
    def is_morale_low(self, morale_days):
        return  self.low_morale >= morale_days
    
    def get_cause_of_death(self, cfg_low_food, cfg_low_morale):
        if not self.is_alive():
            self.cause_of_death = "Injury"
        elif self.is_food_low(cfg_low_food["low_food_death_days"]):
            self.cause_of_death = "Starvation"
        elif self.is_morale_low(cfg_low_morale["low_morale_death_days"]):
            self.cause_of_death = "Hopelessness"