from gladiator import Gladiator
from random import sample

if __name__ == '__main__':
    ## Set Test Parameters
    num_weapons = 10
    num_opponents = 5
    num_rounds = 10
    guess_limit = 7
    
    guess_count = 0
    win_count = 0

    while win_count < num_rounds:
        print()
        print("Starting Round: " + str(win_count + 1))
        code = tuple(sample(range(num_weapons), num_opponents))
        code_set = set(code)

        print("Code is: {}".format(code))
        hercules = Gladiator(num_weapons, num_opponents)
        guess = hercules.get_next_guess()
        guess_count = 1
        won = False

        
        while guess_count <= guess_limit:
            print("Guessed: {}".format(guess))
            num_weps = 0
            num_pos = 0
            
            for i in range(num_opponents):
                if guess[i] in code_set:
                    num_weps += 1
                    if guess[i] == code[i]:
                        num_pos += 1

            if num_pos == num_opponents:
                won = True
                break

            print("Response: {}".format((num_weps, num_pos)))
            hercules.update((num_weps, num_pos))
            guess = hercules.get_next_guess()
            guess_count += 1

        if won:
            win_count += 1
        else:
            raise AssertionError("Failed Round {}. Too many Guesses.".format(win_count + 1))

    print("Test Passed")
