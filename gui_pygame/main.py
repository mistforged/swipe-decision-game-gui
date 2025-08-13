# gui_pygame/main.py
import sys
import pygame

# ---- Engine API ----
from engine.game import (
    start_run,
    get_today_scenario,
    apply_choice,
    is_over,
    final_score,
)

# --------------- Pygame setup ---------------
WIDTH, HEIGHT = 900, 600
FPS = 60

pygame.init()
pygame.display.set_caption("Swipe Decision Game — GUI")
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()

# Fonts
FONT_SM = pygame.font.SysFont("consolas", 18)
FONT_MD = pygame.font.SysFont("consolas", 24)
FONT_LG = pygame.font.SysFont("consolas", 36)
FONT_XL = pygame.font.SysFont("consolas", 52, bold=True)

# Colors
BG      = pygame.Color(22, 22, 28)
PANEL   = pygame.Color(30, 30, 38)
TEXT    = pygame.Color(230, 230, 235)
MUTED   = pygame.Color(170, 170, 180)
ACCENT  = pygame.Color(98, 155, 255)
OK      = pygame.Color(70, 200, 120)
BAD     = pygame.Color(220, 80, 80)
WARN    = pygame.Color(240, 190, 90)
PURPLE  = pygame.Color(170, 120, 255)
WHITE   = pygame.Color(255, 255, 255)
BLACK   = pygame.Color(0, 0, 0)


# --- HUD with flashable bars ---
class StatBar:
    def __init__(self, label, get_pair, rect, base_color, text_color):
        """
        get_pair: callable -> (value, max_value)
        rect: (x, y, w, h)
        """
        self.label = label
        self.get_pair = get_pair
        self.rect = pygame.Rect(rect)
        self.base_color = base_color
        self.text_color = text_color

        # flash state
        self.flash_t = 0.0          # time remaining (seconds)
        self.flash_color = base_color
        self.flash_duration = 1    # how long to flash

    def flash(self, delta):
        if delta == 0:
            return
        # green for positive, red for negative
        self.flash_color = OK if delta > 0 else BAD
        self.flash_t = self.flash_duration

    def update(self, dt):
        if self.flash_t > 0:
            self.flash_t = max(0.0, self.flash_t - dt)

    def _mix_color(self):
        """
        Blend from flash_color back to base_color as flash time elapses.
        t=flash_duration -> flash_color, t=0 -> base_color
        """
        if self.flash_t <= 0:
            return self.base_color
        alpha = self.flash_t / self.flash_duration  # 1..0
        # pygame.Color.lerp(dst, factor) mixes toward dst by factor (0..1)
        # We want: near end -> close to base_color
        return self.flash_color.lerp(self.base_color, 1.0 - alpha)

    def draw(self, surf):
        x, y, w, h = self.rect
        val, mx = self.get_pair()
        pct = 0 if mx <= 0 else max(0.0, min(1.0, val / mx))

        # frame
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=8)

        # fill
        color = self._mix_color()
        fill_w = int((w - 4) * pct)
        if fill_w > 0:
            pygame.draw.rect(surf, color, (x + 2, y + 2, fill_w, h - 4), border_radius=8)

        # label
        txt = FONT_SM.render(f"{self.label}: {val}/{mx}", True, self.text_color)
        surf.blit(txt, (x + 8, y + h // 2 - txt.get_height() // 2))

class HUD:
    def __init__(self, state):
        self.state = state
        p = self.state.player

        # Bars get value providers (lambdas read live values from player)
        self.hp_bar = StatBar("HP",    lambda: (p.hp,    p.hp_max),    (60,  90, 240, 28), OK,    TEXT)
        self.food_bar = StatBar("Food",  lambda: (p.food,  p.food_max),  (330, 90, 240, 28), WARN,  TEXT)
        self.mor_bar = StatBar("Morale",lambda: (p.morale,p.morale_max),(600, 90, 240, 28), ACCENT,TEXT)

        self.bars = [self.hp_bar, self.food_bar, self.mor_bar]

    def update(self, dt):
        for b in self.bars:
            b.update(dt)

    def draw(self, surf):
        self.hp_bar.draw(surf)
        self.food_bar.draw(surf)
        self.mor_bar.draw(surf)

    def flash_from_deltas(self, hp_delta=0, food_delta=0, morale_delta=0):
        if hp_delta:
            self.hp_bar.flash(hp_delta)
        if food_delta:
            self.food_bar.flash(food_delta)
        if morale_delta:
            self.mor_bar.flash(morale_delta)



# --------------- Small UI helpers ---------------
class Button:
    def __init__(self, rect, label, on_click, color=ACCENT):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.color = color

    def draw(self, surf):
        mouse = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse)
        c = self.color.lerp(WHITE, 0.15) if hovering else self.color
        pygame.draw.rect(surf, c, self.rect, border_radius=10)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=10)
        text = FONT_MD.render(self.label, True, WHITE)
        surf.blit(text, text.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()


def draw_text_wrapped(surf, text, font, color, rect, line_height=4):
    """Draw paragraph text inside a rect; returns bottom y."""
    x, y, w, h = rect
    words = text.split(" ")
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if font.size(test)[0] <= w:
            line = test
        else:
            img = font.render(line, True, color)
            surf.blit(img, (x, y))
            y += img.get_height() + line_height
            line = word
    if line:
        img = font.render(line, True, color)
        surf.blit(img, (x, y))
        y += img.get_height()
    return y


def draw_bar(surf, x, y, w, h, value, max_value, color, label):
    # Frame
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2, border_radius=8)
    # Fill
    pct = 0 if max_value <= 0 else max(0, min(1, value / max_value))
    fill_w = int((w - 4) * pct)
    pygame.draw.rect(surf, color, (x + 2, y + 2, fill_w, h - 4), border_radius=8)
    # Label
    txt = FONT_SM.render(f"{label}: {value}/{max_value}", True, TEXT)
    surf.blit(txt, (x + 8, y + h // 2 - txt.get_height() // 2))


# --------------- Scene Manager ---------------
class Scene:
    def handle_event(self, event): ...
    def update(self, dt): ...
    def draw(self, surf): ...

class SceneManager:
    def __init__(self, start_scene):
        self.scene = start_scene

    def switch(self, new_scene):
        self.scene = new_scene

    def handle_event(self, event):
        self.scene.handle_event(event)

    def update(self, dt):
        self.scene.update(dt)

    def draw(self, surf):
        self.scene.draw(surf)


# --------------- Scenes ---------------
class MainMenu(Scene):
    def __init__(self, manager):
        self.mgr = manager
        self.selected = "normal"  # default
        # Buttons
        cx = WIDTH // 2
        self.btn_easy = Button((cx - 280, 360, 160, 48), "Easy",   lambda: self.start("easy"))
        self.btn_norm = Button((cx - 80,  360, 160, 48), "Normal", lambda: self.start("normal"))
        self.btn_hard = Button((cx + 120, 360, 160, 48), "Hard",   lambda: self.start("hard"))

    def start(self, difficulty):
        self.mgr.switch(GameScene(self.mgr, difficulty))

    def handle_event(self, event):
        self.btn_easy.handle(event)
        self.btn_norm.handle(event)
        self.btn_hard.handle(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_e):
                self.start("easy")
            elif event.key in (pygame.K_2, pygame.K_n, pygame.K_RETURN):
                self.start("normal")
            elif event.key in (pygame.K_3, pygame.K_h):
                self.start("hard")

    def update(self, dt): pass

    def draw(self, surf):
        surf.fill(BG)
        title = FONT_XL.render("Swipe Decision Game", True, WHITE)
        sub   = FONT_MD.render("Pick a difficulty to start", True, MUTED)
        surf.blit(title, title.get_rect(center=(WIDTH//2, 160)))
        surf.blit(sub,   sub.get_rect(center=(WIDTH//2, 210)))
        self.btn_easy.draw(surf)
        self.btn_norm.draw(surf)
        self.btn_hard.draw(surf)


class GameScene(Scene):
    def __init__(self, manager, difficulty):
        self.mgr = manager
        self.difficulty = difficulty
        # Start engine run
        self.state = start_run(difficulty)
        self.hud = HUD(self.state)
        self.scenario = get_today_scenario(self.state)
        self.outcome_log = []  # last few strings for HUD
        # Buttons
        self.btn_left  = Button((120, 480, 280, 56), "Left  (←)",  lambda: self.choose("L"))
        self.btn_right = Button((WIDTH-120-280, 480, 280, 56), "Right (→)", lambda: self.choose("R"))

    # Input handlers
    def handle_event(self, event):
        self.btn_left.handle(event)
        self.btn_right.handle(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.choose("L")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.choose("R")

    def choose(self, side):
        if is_over(self.state):
            return
        outcome = apply_choice(self.state, side)

        eff = outcome["effect"]  # {'hp': Δ, 'food': Δ, 'morale': Δ}
        self.hud.flash_from_deltas(eff.get("hp", 0), eff.get("food", 0), eff.get("morale", 0))


        # Build a short line for the on-screen log
        eff = outcome["effect"]
        result = outcome["result"]
        tag = "✓" if result == "success" else ("×" if result == "failure" else "•")
        line = f"{tag} {outcome['log_text']} (HP {eff['hp']:+}, Food {eff['food']:+}, Morale {eff['morale']:+})"
        self.outcome_log.append(line)
        self.outcome_log = self.outcome_log[-6:]  # keep last 6 lines

        # Surprise
        if outcome["surprise"]:
            self.outcome_log.append(f"★ {outcome['surprise']['text']}")
            self.outcome_log = self.outcome_log[-6:]

        # Transition?
        if outcome["death"] or outcome["won"]:
            score = final_score(self.state)
            self.mgr.switch(GameOverScene(self.mgr, self.state, score))
        else:
            # fetch next scenario for the new day
            self.scenario = get_today_scenario(self.state)

    def update(self, dt): 
        self.hud.update(dt)

    def draw(self, surf):
        surf.fill(BG)

        # Panels
        pygame.draw.rect(surf, PANEL, (40, 40, WIDTH-80, 120), border_radius=12)     # HUD panel
        pygame.draw.rect(surf, PANEL, (40, 180, WIDTH-80, 280), border_radius=12)    # Scenario panel
        pygame.draw.rect(surf, PANEL, (40, 470, WIDTH-80, 90), border_radius=12)     # Buttons panel

        # Header
        head = FONT_LG.render(f"Day {self.state.day}/{self.state.num_days} — {self.difficulty.title()}", True, TEXT)
        surf.blit(head, (60, 52))

        # Bars
        p = self.state.player
        #draw_bar(surf, 60, 90, 240, 28, p.hp,    p.hp_max,    OK,   "HP")
        #draw_bar(surf, 330,90, 240, 28, p.food,  p.food_max,  WARN, "Food")
        #draw_bar(surf, 600,90, 240, 28, p.morale,p.morale_max,ACCENT,"Morale")
        self.hud.draw(surf)

        # Scenario text + options
        y = draw_text_wrapped(
            surf,
            self.scenario["description"],
            FONT_MD, TEXT,
            (60, 200, WIDTH-120, 130),
        )
        surf.blit(FONT_MD.render("L: " + self.scenario["left_choice"]["text"], True, WHITE), (60, y + 10))
        surf.blit(FONT_MD.render("R: " + self.scenario["right_choice"]["text"], True, WHITE), (60, y + 44))
        surf.blit(FONT_SM.render("Press ← / → or click a button", True, MUTED), (60, y + 74))

        # Buttons
        self.btn_left.draw(surf)
        self.btn_right.draw(surf)

        # Recent outcome log (bottom-left)
        ly = 470 - 88
        for line in self.outcome_log[-5:]:
            color = TEXT
            if line.startswith("✓"): color = OK
            elif line.startswith("×"): color = BAD
            elif line.startswith("★"): color = PURPLE
            img = FONT_SM.render(line, True, color)
            surf.blit(img, (60, ly))
            ly += img.get_height() + 4


class GameOverScene(Scene):
    def __init__(self, manager, state, score):
        self.mgr = manager
        self.score = score
        self.won = state.won
        self.cause = state.cause_of_death
        self.difficulty = state.difficulty
        self.days = state.day if state.over else max(0, state.day - 1)
        # Buttons
        cx = WIDTH // 2
        self.btn_again = Button((cx - 240, 420, 200, 56), "Play Again", lambda: self.mgr.switch(MainMenu(self.mgr)))
        self.btn_menu  = Button((cx + 40,  420, 200, 56), "Main Menu",  lambda: self.mgr.switch(MainMenu(self.mgr)))

    def handle_event(self, event):
        self.btn_again.handle(event)
        self.btn_menu.handle(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.mgr.switch(MainMenu(self.mgr))

    def update(self, dt): pass

    def draw(self, surf):
        surf.fill(BG)
        title = "Victory!" if self.won else "Game Over"
        color = OK if self.won else BAD
        t_img = FONT_XL.render(title, True, color)
        surf.blit(t_img, t_img.get_rect(center=(WIDTH//2, 140)))

        # Stats
        y = 220
        lines = [
            f"Difficulty: {self.difficulty.title()}",
            f"Days Survived: {self.days}",
            f"Cause: {self.cause if self.cause!='None' else '—'}",
            f"Final Score: {self.score}",
        ]
        for line in lines:
            img = FONT_MD.render(line, True, TEXT)
            surf.blit(img, img.get_rect(center=(WIDTH//2, y)))
            y += 36

        self.btn_again.draw(surf)
        self.btn_menu.draw(surf)


# --------------- Main loop ---------------
def main():
    manager = SceneManager(MainMenu(None))
    manager.scene.mgr = manager  # late bind (so scenes can switch)

    while True:
        dt = CLOCK.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            manager.handle_event(event)

        manager.update(dt)
        manager.draw(SCREEN)
        pygame.display.flip()


if __name__ == "__main__":
    main()
