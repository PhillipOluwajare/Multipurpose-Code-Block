import random
import json
import os
import hashlib
from datetime import datetime
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

HISTORY_FILE = 'game_history.json'
PASSWORD_FILE = 'password.txt'
password_hash = None

# ---------------- Password Functions ----------------
def reset_password():
    """Reset the program password after verifying the old one."""
    vef_pass()
    print(Fore.CYAN + Style.BRIGHT + "\n--- Reset Password ---")
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
    if hash_password(pass_ent) == saved_hash:
        print(Fore.GREEN + 'Password verified. You can continue.')
    else:
        print(Fore.RED + 'Incorrect password. Exiting program...')
        exit()

# ---------------- History Functions ----------------
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

game_history = load_history()

def save_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(game_history, f, indent=4)

def show_history():
    vef_pass()
    if not game_history:
        print(Fore.RED + '\nNo games played yet.')
        return
    print(Fore.CYAN + Style.BRIGHT + '\n--- Game History ---')
    for i, entry in enumerate(game_history, 1):
        # Color result
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
              f"{Fore.WHITE}| Rounds: {entry['rounds']}")
    print(Fore.CYAN + '--------------------')

def clear_history():
    global game_history
    vef_pass()
    if not game_history:
        print(Fore.RED + 'No history to clear.')
        return
    confirm = input(Fore.YELLOW + "Are you sure you want to delete all saved history? (yes/no): ").strip().lower()
    if confirm == 'yes':
        game_history = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        print(Fore.GREEN + "History cleared successfully.")
    else:
        print(Fore.WHITE + "Canceled. History not deleted.")

# ---------------- Calculator ----------------
def calc():
    print(Fore.CYAN + Style.BRIGHT + '\nWelcome to the calculator.')
    while True:
        op = input(Fore.YELLOW + 'Enter operation (add, sub, mul, div) or "exit": ').strip().lower()
        if op == 'exit':
            break
        if op not in ['add', 'sub', 'mul', 'div']:
            print(Fore.RED + 'Invalid operation.')
            continue
        try:
            a = float(input(Fore.YELLOW + 'Enter first number: '))
            b = float(input(Fore.YELLOW + 'Enter second number: '))
        except ValueError:
            print(Fore.RED + 'Invalid input. Please enter numbers.')
            continue
        if op == 'add':
            result = a + b
        elif op == 'sub':
            result = a - b
        elif op == 'mul':
            result = a * b
        elif op == 'div':
            if b == 0:
                print(Fore.RED + 'Error: Division by zero.')
                continue
            result = a / b
        print(Fore.GREEN + f'Result: {result}')

# ---------------- Rock Paper Scissors ----------------
def rock_paper_scissors():
    choices = ['rock', 'paper', 'scissors']

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

        while round_num <= round_quest:
            print(Fore.CYAN + f'\n--- Round {round_num} ---')
            user_choice = input(Fore.YELLOW + 'Enter rock, paper, or scissors (or "exit"): ').strip().lower()
            if user_choice == 'exit':
                break

            if user_choice not in choices and user_choice not in ['r', 'p', 's']:
                print(Fore.RED + 'Invalid choice. Try again.')
                continue  # Don't advance round number

            computer_choice = random.choice(choices)
            print(Fore.WHITE + f'Computer chose: {computer_choice}')

            if user_choice == computer_choice:
                print(Fore.YELLOW + '🤝 Tie!')
            elif (user_choice in ['rock', 'r'] and computer_choice == 'scissors') or \
                 (user_choice in ['paper', 'p'] and computer_choice == 'rock') or \
                 (user_choice in ['scissors', 's'] and computer_choice == 'paper'):
                print(Fore.GREEN + '✅ You win this round!')
                score += 1
            else:
                print(Fore.RED + '❌ Computer wins this round!')
                comp_score += 1

            round_num += 1

        # Game result
        if score > comp_score:
            result = 'Win'
            print(Fore.GREEN + '\n🎉 You won the game!')
        elif score < comp_score:
            result = 'Loss'
            print(Fore.RED + '\n💀 You lost the game.')
        else:
            result = 'Tie'
            print(Fore.YELLOW + '\n🤝 It\'s a tie!')

        game_history.append({
            'result': result,
            'you': score,
            'computer': comp_score,
            'rounds': round_quest,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        save_history()

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
        prog_choice = input(Fore.YELLOW +
                            'Options: Calc, Rock Paper Scissors, History, Clear History, Reset Password or Exit: ').strip().lower()
        if prog_choice == 'exit':
            print(Fore.GREEN + 'Thank you for using the multitasking program. Goodbye!')
            break
        elif prog_choice == 'calc':
            calc()
        elif prog_choice in ['rock paper scissors', 'rps']:
            rock_paper_scissors()
        elif prog_choice == 'history':
            show_history()
        elif prog_choice == 'clear history':
            clear_history()
        elif prog_choice == 'reset password':
            reset_password()
        else:
            print(Fore.RED + 'Invalid choice. Please try again.')

# ---------------- Program Start ----------------
if not os.path.exists(PASSWORD_FILE):
    password_hash = pass_word()

main()