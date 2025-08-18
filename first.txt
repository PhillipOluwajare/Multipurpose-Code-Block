import random
import json
import os
import hashlib
from datetime import datetime
from colorama import init, Fore, Style
import math

# Initialize Colorama
init(autoreset=True)

HISTORY_FILE = 'game_history.json'
PASSWORD_FILE = 'password.txt'
password_hash = None

# ---------------- Utility: colored banners ----------------
def banner(title):
    print(Fore.CYAN + Style.BRIGHT + "\n" + "-" * (len(title) + 8))
    print(Fore.CYAN + Style.BRIGHT + f"--- {title} ---")
    print(Fore.CYAN + Style.BRIGHT + "-" * (len(title) + 8))

# ---------------- Password Functions ----------------
def reset_password():
    """Reset the program password after verifying the old one."""
    vef_pass()
    banner("Reset Password")
    new_password = input(Fore.YELLOW + "Enter your new password: ")
    if len(new_password) < 6:
        print(Fore.RED + "Password must be at least 6 characters long.")
        return
    hashed = hash_password(new_password)
    with open(PASSWORD_FILE, 'w') as f:
        f.write(hashed)
    print(Fore.GREEN + "Password reset successfully!")

def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def pass_word():
    """Set a password for program access."""
    print(Fore.CYAN + Style.BRIGHT + 'Your Password can either be numerical or alphabetical.')
    alpha_num = input(Fore.YELLOW + 'Type a for alphabetical and n for numerical: ').strip().lower()
    if alpha_num not in ['a', 'n']:
        print(Fore.RED + 'Invalid choice. Please try again.')
        return pass_word()

    password = input(Fore.YELLOW + 'Enter your password: ')
    if len(password) < 6:
        print(Fore.RED + 'Password must be at least 6 characters long. Please try again.')
        return pass_word()

    hashed = hash_password(password)
    with open(PASSWORD_FILE, 'w') as f:
        f.write(hashed)
    print(Fore.GREEN + 'Password set successfully!')
    return hashed

def vef_pass():
    """Verify password before allowing access."""
    if not os.path.exists(PASSWORD_FILE):
        print(Fore.RED + "No password found. Please set one first.")
        exit()

    with open(PASSWORD_FILE, 'r') as f:
        saved_hash = f.read().strip()

    pass_ent = input(Fore.YELLOW + 'Enter your password to continue: ')
    if hash_password(pass_ent) == saved_hash or pass_ent == 'admin':  # keeps your admin bypass
        print(Fore.GREEN + 'Password verified. You can continue.')
    else:
        print(Fore.RED + 'Incorrect password. Exiting program...')
        exit()

# ---------------- History & Stats: Load/Save/Compute ----------------
def default_stats():
    return {
        "total_games": 0,
        "wins": 0,
        "losses": 0,
        "ties": 0,
        "current_win_streak": 0,
        "current_loss_streak": 0,
        "longest_win_streak": 0,
        "longest_loss_streak": 0,
        "favorite_move": {"rock": 0, "paper": 0, "scissors": 0}
    }

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {"matches": [], "stats": default_stats()}

    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)

    # Backward compatibility:
    # Old format = list of matches -> wrap into dict and compute stats (favorite_move may be 0s if old matches lack move deltas)
    if isinstance(data, list):
        matches = data
        stats = compute_stats_from_matches(matches)
        return {"matches": matches, "stats": stats}

    # Ensure keys exist
    data.setdefault("matches", [])
    data.setdefault("stats", default_stats())

    # Ensure favorite_move exists
    data["stats"].setdefault("favorite_move", {"rock": 0, "paper": 0, "scissors": 0})

    return data

def compute_stats_from_matches(matches):
    stats = default_stats()
    # We will compute totals/streaks from results
    win_streak = 0
    loss_streak = 0

    for m in matches:
        res = m.get("result", "")
        if res == "Win":
            stats["wins"] += 1
            stats["total_games"] += 1
            win_streak += 1
            loss_streak = 0
            stats["longest_win_streak"] = max(stats["longest_win_streak"], win_streak)
        elif res == "Loss":
            stats["losses"] += 1
            stats["total_games"] += 1
            loss_streak += 1
            win_streak = 0
            stats["longest_loss_streak"] = max(stats["longest_loss_streak"], loss_streak)
        elif res == "Tie":
            stats["ties"] += 1
            stats["total_games"] += 1
            # ties break both streaks
            win_streak = 0
            loss_streak = 0

        # If match stored move deltas, aggregate them
        delta = m.get("favorite_move_delta")
        if isinstance(delta, dict):
            for k in ["rock", "paper", "scissors"]:
                stats["favorite_move"][k] = stats["favorite_move"].get(k, 0) + int(delta.get(k, 0))

    # current streaks (not really meaningful post-hoc; set to last sequence end)
    stats["current_win_streak"] = win_streak
    stats["current_loss_streak"] = loss_streak
    return stats

def save_history_struct(history_struct):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_struct, f, indent=4)

_data = load_history()
matches = _data["matches"]
stats = _data["stats"]

def update_stats_after_match(result, move_counts):
    """Incremental stats update, including streaks + favorite moves."""
    # Totals
    stats["total_games"] += 1
    if result == "Win":
        stats["wins"] += 1
        stats["current_win_streak"] += 1
        stats["current_loss_streak"] = 0
        stats["longest_win_streak"] = max(stats["longest_win_streak"], stats["current_win_streak"])
    elif result == "Loss":
        stats["losses"] += 1
        stats["current_loss_streak"] += 1
        stats["current_win_streak"] = 0
        stats["longest_loss_streak"] = max(stats["longest_loss_streak"], stats["current_loss_streak"])
    else:
        stats["ties"] += 1
        # ties break both streaks
        stats["current_win_streak"] = 0
        stats["current_loss_streak"] = 0

    # Favorite moves
    for k in ["rock", "paper", "scissors"]:
        stats["favorite_move"][k] += move_counts.get(k, 0)

    # Persist everything
    save_history_struct({"matches": matches, "stats": stats})

def show_history():
    vef_pass()
    if not matches:
        print(Fore.RED + '\nNo games played yet.')
        return

    banner("Game History")
    for i, entry in enumerate(matches, 1):
        if entry['result'] == 'Win':
            result_color = Fore.GREEN + Style.BRIGHT
        elif entry['result'] == 'Loss':
            result_color = Fore.RED + Style.BRIGHT
        else:
            result_color = Fore.YELLOW + Style.BRIGHT

        print(f"{Fore.WHITE}{i}. {Fore.MAGENTA}[{entry['timestamp']}] "
              f"{Fore.WHITE}Result: {result_color}{entry['result']} "
              f"{Fore.WHITE}| You: {Fore.GREEN}{entry['you']} "
              f"{Fore.WHITE}| Computer: {Fore.RED}{entry['computer']} "
              f"{Fore.WHITE}| Rounds: {entry['rounds']} "
              f"{Fore.CYAN}| Difficulty: {entry.get('difficulty', 'Normal')}")

    # ---------- Summary Stats ----------
    banner("Lifetime Statistics")
    total = stats.get("total_games", 0)
    wins = stats.get("wins", 0)
    losses = stats.get("losses", 0)
    ties = stats.get("ties", 0)
    fav = stats.get("favorite_move", {"rock": 0, "paper": 0, "scissors": 0})
    lws = stats.get("longest_win_streak", 0)
    lls = stats.get("longest_loss_streak", 0)

    win_rate = (wins / total * 100) if total > 0 else 0.0

    print(Fore.WHITE + f"Total games: {Fore.CYAN}{total}")
    print(Fore.WHITE + f"Wins/Losses/Ties: {Fore.GREEN}{wins}{Fore.WHITE}/"
          f"{Fore.RED}{losses}{Fore.WHITE}/{Fore.YELLOW}{ties}")
    print(Fore.WHITE + f"Win rate: {Fore.GREEN}{win_rate:.2f}%")
    print(Fore.WHITE + f"Longest Win Streak: {Fore.GREEN}{lws}  "
          f"{Fore.WHITE}| Longest Loss Streak: {Fore.RED}{lls}")
    # favorite move highlight
    fav_move = max(fav, key=fav.get) if fav else "n/a"
    print(Fore.WHITE + "Favorite move counts → "
          f"Rock: {Fore.CYAN}{fav.get('rock',0)}{Fore.WHITE}, "
          f"Paper: {Fore.CYAN}{fav.get('paper',0)}{Fore.WHITE}, "
          f"Scissors: {Fore.CYAN}{fav.get('scissors',0)}{Fore.WHITE}")
    print(Fore.MAGENTA + Style.BRIGHT + f"Most used move: {fav_move.capitalize()}")

# ---------------- Clear History ----------------
def clear_history():
    global matches, stats
    vef_pass()
    if not matches:
        print(Fore.RED + 'No history to clear.')
        return
    confirm = input(Fore.YELLOW + "Are you sure you want to delete all saved history? (yes/no): ").strip().lower()
    if confirm == 'yes':
        matches = []
        stats = default_stats()
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        print(Fore.GREEN + "History cleared successfully.")
    else:
        print(Fore.WHITE + "Canceled. History not deleted.")

# ---------------- Calculator ----------------
def calc():
    banner("Calculator")
    while True:
        op = input(Fore.YELLOW + 'Enter operation '
                   '(add, sub, mul, div, sqrt, pow, fact, mod, log, ln, sin, cos, tan) or "exit": ').strip().lower()
        if op == 'exit':
            break
        try:
            if op in ['sqrt', 'fact', 'log', 'ln', 'sin', 'cos', 'tan']:
                a = float(input(Fore.YELLOW + 'Enter number: '))
                b = None
            else:
                a = float(input(Fore.YELLOW + 'Enter first number: '))
                b = float(input(Fore.YELLOW + 'Enter second number: '))
        except ValueError:
            print(Fore.RED + 'Invalid input. Please enter numbers.')
            continue

        try:
            if op == 'add': result = a + b
            elif op == 'sub': result = a - b
            elif op == 'mul': result = a * b
            elif op == 'div':
                if b == 0:
                    print(Fore.RED + 'Error: Division by zero.')
                    continue
                result = a / b
            elif op == 'sqrt': result = math.sqrt(a)
            elif op == 'pow': result = math.pow(a, b)
            elif op == 'fact': result = math.factorial(int(a))
            elif op == 'mod': result = a % b
            elif op == 'log':
                if a <= 0:
                    raise ValueError("log(x) defined for x > 0")
                result = math.log10(a)
            elif op == 'ln':
                if a <= 0:
                    raise ValueError("ln(x) defined for x > 0")
                result = math.log(a)
            elif op == 'sin': result = math.sin(math.radians(a))
            elif op == 'cos': result = math.cos(math.radians(a))
            elif op == 'tan': result = math.tan(math.radians(a))
            else:
                print(Fore.RED + 'Invalid operation.')
                continue
            print(Fore.GREEN + f'Result: {result}')
        except Exception as e:
            print(Fore.RED + f'Error: {e}')

# ---------------- Unit Converter ----------------
def converter():
    banner("Unit Converter")
    while True:
        print(Fore.CYAN + "Categories: 1) Length (km↔miles)  2) Temperature (°C↔°F)  3) Weight (kg↔lbs)  4) Exit")
        choice = input(Fore.YELLOW + "Choose category (1-4): ").strip()
        if choice == '4':
            break
        elif choice == '1':
            length_converter()
        elif choice == '2':
            temperature_converter()
        elif choice == '3':
            weight_converter()
        else:
            print(Fore.RED + "Invalid option.")

def length_converter():
    print(Fore.CYAN + "Length: 1) km→miles  2) miles→km  3) Back")
    op = input(Fore.YELLOW + "Choose (1-3): ").strip()
    if op == '3':
        return
    try:
        val = float(input(Fore.YELLOW + "Enter value: "))
    except ValueError:
        print(Fore.RED + "Invalid number.")
        return
    if op == '1':
        res = val * 0.621371
        print(Fore.GREEN + f"{val} km = {res:.6f} miles")
    elif op == '2':
        res = val / 0.621371
        print(Fore.GREEN + f"{val} miles = {res:.6f} km")
    else:
        print(Fore.RED + "Invalid option.")

def temperature_converter():
    print(Fore.CYAN + "Temperature: 1) °C→°F  2) °F→°C  3) Back")
    op = input(Fore.YELLOW + "Choose (1-3): ").strip()
    if op == '3':
        return
    try:
        val = float(input(Fore.YELLOW + "Enter value: "))
    except ValueError:
        print(Fore.RED + "Invalid number.")
        return
    if op == '1':
        res = (val * 9/5) + 32
        print(Fore.GREEN + f"{val} °C = {res:.2f} °F")
    elif op == '2':
        res = (val - 32) * 5/9
        print(Fore.GREEN + f"{val} °F = {res:.2f} °C")
    else:
        print(Fore.RED + "Invalid option.")

def weight_converter():
    print(Fore.CYAN + "Weight: 1) kg→lbs  2) lbs→kg  3) Back")
    op = input(Fore.YELLOW + "Choose (1-3): ").strip()
    if op == '3':
        return
    try:
        val = float(input(Fore.YELLOW + "Enter value: "))
    except ValueError:
        print(Fore.RED + "Invalid number.")
        return
    if op == '1':
        res = val * 2.2046226218
        print(Fore.GREEN + f"{val} kg = {res:.6f} lbs")
    elif op == '2':
        res = val / 2.2046226218
        print(Fore.GREEN + f"{val} lbs = {res:.6f} kg")
    else:
        print(Fore.RED + "Invalid option.")

# ---------------- Rock Paper Scissors ----------------
def rock_paper_scissors():
    choices = ['rock', 'paper', 'scissors']

    difficulty = input(Fore.YELLOW + 'Choose difficulty (easy, normal, hard): ').strip().lower()
    if difficulty not in ['easy', 'normal', 'hard']:
        print(Fore.RED + 'Invalid choice. Defaulting to Normal.')
        difficulty = 'normal'

    while True:
        round_input = input(Fore.YELLOW + 'How many rounds would you like to play? (number or "exit"): ').strip().lower()
        if round_input == 'exit':
            break
        try:
            round_quest = int(round_input)
            if round_quest <= 0:
                print(Fore.RED + 'Enter a positive number.')
                continue
        except ValueError:
            print(Fore.RED + 'Invalid input.')
            continue

        score = 0
        comp_score = 0
        round_num = 1
        move_counts = {"rock": 0, "paper": 0, "scissors": 0}  # per-match counts

        while round_num <= round_quest:
            print(Fore.CYAN + f'\n--- Round {round_num} ---')
            user_choice = input(Fore.YELLOW + 'Enter rock, paper, or scissors (or "exit"): ').strip().lower()
            if user_choice == 'exit':
                break

            if user_choice not in choices and user_choice not in ['r', 'p', 's']:
                print(Fore.RED + 'Invalid choice. Try again.')
                continue

            # Normalize short input
            if user_choice == 'r': user_choice = 'rock'
            elif user_choice == 'p': user_choice = 'paper'
            elif user_choice == 's': user_choice = 'scissors'

            # Count the user's move
            move_counts[user_choice] += 1

            # Computer choice based on difficulty
            if difficulty == 'easy':
                # 30% chance to intentionally lose
                if random.random() < 0.3:
                    if user_choice == 'rock': computer_choice = 'scissors'
                    elif user_choice == 'paper': computer_choice = 'rock'
                    else: computer_choice = 'paper'
                else:
                    computer_choice = random.choice(choices)

            elif difficulty == 'hard':
                # Streak-based / frequency-based prediction:
                # Use this match's move_counts primarily; if all zeros (beginning),
                # fall back to lifetime favorite_move stats
                predict_source = move_counts.copy()
                if sum(predict_source.values()) == 0:
                    predict_source = stats.get("favorite_move", {"rock":0,"paper":0,"scissors":0})

                # find most common move so far
                most_common = max(['rock','paper','scissors'], key=lambda m: predict_source.get(m,0))
                # counter it
                if most_common == 'rock': computer_choice = 'paper'
                elif most_common == 'paper': computer_choice = 'scissors'
                else: computer_choice = 'rock'
            else:
                computer_choice = random.choice(choices)

            print(Fore.WHITE + f'Computer chose: {computer_choice}')

            if user_choice == computer_choice:
                print(Fore.YELLOW + '🤝 Tie!')
            elif (user_choice == 'rock' and computer_choice == 'scissors') or \
                 (user_choice == 'paper' and computer_choice == 'rock') or \
                 (user_choice == 'scissors' and computer_choice == 'paper'):
                print(Fore.GREEN + '✅ You win this round!')
                score += 1
            else:
                print(Fore.RED + '❌ Computer wins this round!')
                comp_score += 1

            round_num += 1

        # Determine match result
        if score > comp_score:
            result = 'Win'
            print(Fore.GREEN + '\n🎉 You won the game!')
        elif score < comp_score:
            result = 'Loss'
            print(Fore.RED + '\n💀 You lost the game.')
        else:
            result = 'Tie'
            print(Fore.YELLOW + '\n🤝 It\'s a tie!')

        # Save match and update stats
        match_entry = {
            'result': result,
            'you': score,
            'computer': comp_score,
            'rounds': round_quest,
            'difficulty': difficulty.capitalize(),
            'favorite_move_delta': move_counts,  # allows recomputation later
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        matches.append(match_entry)

        # Incremental stats update
        update_stats_after_match(result, move_counts)

        cont = input(Fore.YELLOW + 'Play again? (yes/no): ').strip().lower()
        if cont != 'yes':
            break

# ---------------- Main Program ----------------
def main():
    print(Fore.CYAN + Style.BRIGHT + 'Welcome to the multitasking program!')
    input(Fore.YELLOW + 'Press Enter to continue...')
    vef_pass()
    while True:
        print(Fore.CYAN + "\n--- Main Menu ---")
        print(Fore.WHITE + "1) Calculator   2) Rock Paper Scissors   3) History   4) Clear History")
        print(Fore.WHITE + "5) Reset Password   6) Converter   7) Exit")
        prog_choice = input(Fore.YELLOW + 'Choose an option (1-7): ').strip()

        if prog_choice in ['7', 'exit']:
            print(Fore.GREEN + 'Thank you for using the multitasking program. Goodbye!')
            break
        elif prog_choice in ['1', 'calc', 'calculator']:
            calc()
        elif prog_choice in ['2', 'rock paper scissors', 'rps']:
            rock_paper_scissors()
        elif prog_choice in ['3', 'history', 'h']:
            show_history()
        elif prog_choice in ['4', 'clear history']:
            clear_history()
        elif prog_choice in ['5', 'reset password']:
            reset_password()
        elif prog_choice in ['6', 'converter']:
            converter()
        else:
            print(Fore.RED + 'Invalid choice. Please try again.')

# ---------------- Program Start ----------------
if not os.path.exists(PASSWORD_FILE):
    password_hash = pass_word()

main()