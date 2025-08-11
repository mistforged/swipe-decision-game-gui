from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import random

from engine.player import Player
from engine.scenarios import scenarios as SCENARIOS, get_random_event
from engine.config import NUM_DAYS, DIFF_CFG, STARTS, DIFF_SCORE_MULT
from engine.utils import clamp

# ---------- Engine-facing data structures ----------

@dataclass
class GameState:
    difficulty: str
    cfg: Dict[str, Any]
    num_days: int
    day: int
    player: Player
    scenario_order: List[Dict[str, Any]]  # length == num_days
    event_log: List[str] = field(default_factory=list)
    over: bool = False
    cause_of_death: str = "None"
    won: bool = False


# ---------- Public API ----------

def start_run(difficulty: str, num_days: Optional[int] = None) -> GameState:
    """
    Initialize a new run: pick difficulty, create player, and sample a no-repeat scenario order.
    """
    difficulty = difficulty.lower()
    if difficulty not in STARTS:
        difficulty = "normal"

    starts = STARTS[difficulty]
    cfg = DIFF_CFG[difficulty]

    n = num_days if num_days is not None else NUM_DAYS
    if n > len(SCENARIOS):
        raise ValueError("NUM_DAYS exceeds available scenarios.")

    player = Player(
        hp=starts["hp"],
        food=starts["food"],
        morale=starts["morale"],
        hp_max=starts["hp_max"],
        food_max=starts["food_max"],
        morale_max=starts["morale_max"],
        difficulty=difficulty,
    )

    order = random.sample(SCENARIOS, k=n)

    return GameState(
        difficulty=difficulty,
        cfg=cfg,
        num_days=n,
        day=1,
        player=player,
        scenario_order=order,
    )


def get_today_scenario(state: GameState) -> Dict[str, Any]:
    """
    Returns the scenario for the current day. Caller should check is_over() first.
    """
    index = max(0, min(state.day - 1, state.num_days - 1))
    return state.scenario_order[index]


def apply_choice(state: GameState, choice: str) -> Dict[str, Any]:
    """
    Core transition for one day:
    - Resolve player's chosen option (with chance if present)
    - Apply effects
    - Roll & apply surprise
    - Daily decay (food tick, starvation morale cadence)
    - Death checks / win check
    - Advance day if still alive and not yet finished

    Returns an outcome dict that a UI can render directly.
    """
    if state.over:
        return _outcome_stub(state, log_text="Run is already over.")

    choice = choice.upper().strip()
    if choice not in ("L", "R"):
        choice = "L"  # default fallback

    scenario = get_today_scenario(state)
    chosen = scenario["left_choice"] if choice == "L" else scenario["right_choice"]

    # ---- Resolve main effect (chance or flat effects) ----
    if "chance" in chosen:
        p = clamp(chosen["chance"] + state.cfg.get("risk_success_bonus", 0.0), 0.05, 0.95)
        success = (random.random() <= p)
        effect = chosen["success_effects"] if success else chosen["failure_effects"]
        result = "success" if success else "failure"
        log_text = f"{chosen['log_text']} {'Success!' if success else 'Failure...'}"
    else:
        effect = chosen["effects"]
        result = "neutral"
        log_text = chosen["log_text"]

    # ---- Apply main effect ----
    state.player.apply_effects(
        hp=effect.get("hp", 0),
        food=effect.get("food", 0),
        morale=effect.get("morale", 0),
    )

    # ---- Surprise event ----
    surprise_raw = get_random_event(state.cfg.get("surprise_chance", 0.2))
    surprise: Optional[Dict[str, Any]] = None
    if surprise_raw != -1:
        # strip textless keys, so we can use **
        surprise = {
            k: v for k, v in surprise_raw.items()
            if k in ("hp", "food", "morale")
        }
        state.player.apply_effects(
            hp=surprise.get("hp", 0),
            food=surprise.get("food", 0),
            morale=surprise.get("morale", 0),
        )

    # ---- Daily decay ----
    state.player.daily_decay(state.cfg)

    # ---- Compose deltas we just applied (for logging/UI) ----
    effect_delta = {
        "hp": effect.get("hp", 0),
        "food": effect.get("food", 0),
        "morale": effect.get("morale", 0),
    }
    surprise_text: Optional[str] = None
    if surprise_raw != -1:
        surprise_text = surprise_raw["text"]

    # ---- Death & win checks ----
    death: Optional[str] = None
    if not state.player.is_alive():
        death = "Injury"
    elif state.player.low_food >= state.cfg.get("low_food_death_days", 3):
        death = "Starvation"
    elif state.player.low_morale >= state.cfg.get("low_morale_death_days", 3):
        death = "Hopelessness"

    if death:
        state.over = True
        state.won = False
        state.cause_of_death = death
        state.player.cause_of_death = death
    else:
        # Survived the day
        if state.day >= state.num_days:
            state.over = True
            state.won = True
        else:
            state.day += 1

    # ---- Append a compact log line to state (engine keeps a journal, UI may show/ignore) ----
    delta_fmt = f"(HP {effect_delta['hp']:+}, Food {effect_delta['food']:+}, Morale {effect_delta['morale']:+})"
    entry = f"Day {max(1, state.day if state.over else state.day-1)}: {scenario['description']} -> {choice} | {log_text} {delta_fmt}"
    state.event_log.append(entry)
    if surprise_text:
        state.event_log.append(f"    • Surprise: {surprise_text}")

    # ---- Build UI-facing outcome ----
    outcome = {
        "log_text": log_text,
        "result": result,  # "success" | "failure" | "neutral"
        "effect": effect_delta,
        "surprise": {"text": surprise_text} if surprise_text else None,
        "stats_after": {"hp": state.player.hp, "food": state.player.food, "morale": state.player.morale},
        "death": death,          # None or reason
        "won": state.over and state.won,
        "day": state.day,        # current day index after resolution (advanced if survived)
        "num_days": state.num_days,
    }
    return outcome


def is_over(state: GameState) -> bool:
    return state.over


def final_score(state: GameState) -> int:
    """
    Score mirrors your CLI formula, with optional difficulty multiplier.
    """
    # completed days: if run is over, we finished current day; otherwise we've completed day-1
    days_completed = state.day if state.over else max(0, state.day - 1)
    days_completed = max(0, min(days_completed, state.num_days))

    base = (days_completed * 10) + (state.player.hp * 5) + (state.player.food * 2) + (state.player.morale * 5)
    mult = DIFF_SCORE_MULT.get(state.difficulty, 1.0)
    return int(round(base * mult))


# ---------- Helpers ----------

def _outcome_stub(state: GameState, log_text: str) -> Dict[str, Any]:
    return {
        "log_text": log_text,
        "result": "neutral",
        "effect": {"hp": 0, "food": 0, "morale": 0},
        "surprise": None,
        "stats_after": {"hp": state.player.hp, "food": state.player.food, "morale": state.player.morale},
        "death": state.cause_of_death if state.over else None,
        "won": state.over and state.won,
        "day": state.day,
        "num_days": state.num_days,
    }