# cli_runner.py
import sys

# Optional colors (no hard dependency)
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    GREEN, RED, YELLOW, MAGENTA, RESET = Fore.GREEN, Fore.RED, Fore.YELLOW, Fore.MAGENTA, Style.RESET_ALL
except Exception:
    GREEN = RED = YELLOW = MAGENTA = RESET = ""

from engine.game import start_run, get_today_scenario, apply_choice, is_over, final_score


def ask_difficulty() -> str:
    print("\nChoose difficulty: (1) Easy, (2) Normal, (3) Hard")
    while True:
        d = input("Difficulty: ").strip().lower()
        if d in ("1", "easy"):
            return "easy"
        if d in ("2", "normal", ""):
            return "normal"
        if d in ("3", "hard"):
            return "hard"
        print("Please enter 1, 2, or 3 (easy/normal/hard).")


def ask_choice() -> str:
    while True:
        c = input("Swipe Left (L) or Right (R)? ").strip().upper()
        if c in ("L", "R"):
            return c
        print("Please enter L or R.")


def render_stats(stats_after: dict) -> None:
    hp, food, morale = stats_after["hp"], stats_after["food"], stats_after["morale"]
    print(f"\nStats → ❤️ HP: {hp}   🍗 Food: {food}   😇 Morale: {morale}\n")


def main() -> int:
    print("\n=== Swipe Decision Game (CLI smoke test) ===")
    try:
        while True:
            difficulty = ask_difficulty()
            state = start_run(difficulty)

            while not is_over(state):
                # Show header and today's scenario
                print("\n" + "=" * 28)
                print(f"        Day {state.day} / {state.num_days}")
                print("=" * 28)

                s = get_today_scenario(state)
                print(s["description"])
                print("L:", s["left_choice"]["text"])
                print("R:", s["right_choice"]["text"])

                # Player chooses
                choice = ask_choice()

                # Resolve one day
                outcome = apply_choice(state, choice)
                log_text = outcome["log_text"]

                # Color feedback on result
                if outcome["result"] == "success":
                    print(GREEN + log_text + RESET)
                elif outcome["result"] == "failure":
                    print(RED + log_text + RESET)
                else:
                    print(YELLOW + log_text + RESET)

                # Surprise (if any)
                if outcome["surprise"]:
                    print(MAGENTA + "• Surprise: " + outcome["surprise"]["text"] + RESET)

                # Show updated stats
                render_stats(outcome["stats_after"])

                # If run ended this day, break to summary
                if outcome["death"] or outcome["won"]:
                    break

            # Summary
            print("\n=== Run Complete ===")
            if state.won:
                print(GREEN + "Victory! You survived the journey." + RESET)
            elif state.cause_of_death != "None":
                print(RED + f"Game Over — Cause of death: {state.cause_of_death}" + RESET)

            score = final_score(state)
            print(f"Final score: {score}")

            # Quick log preview (last few lines)
            print("\nJournal (last 5):")
            for line in state.event_log[-5:]:
                print("  " + line)

            again = input("\nPlay again? (Y/N): ").strip().upper()
            if again != "Y":
                break

        print("\nFinished testing the engine. End game. 👾")
        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted. Bye!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
