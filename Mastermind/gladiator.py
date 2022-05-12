from itertools import combinations, permutations, chain
from random import sample, shuffle
from math import factorial, comb
from time import time
import pdb

class Gladiator:
    def __init__(self, num_weapons, num_opponents, threshold=4000000):
        self.num_weapons = num_weapons
        self.num_opponents = num_opponents
        self.threshold = threshold

        self.backlog = 0
        self.previous_guesses = []
        self.previous_responses = []
        self.possible_codes = [dict() for _ in range(num_opponents + 1)]
        self.num_perm_per_combo = factorial(num_opponents)
        self.num_combos = comb(num_weapons, num_opponents)

    ## Reset Gladiator to original state
    def reset(self):
        self.backlog = 0
        self.previous_guesses = []
        self.previous_responses = []
        self.possible_codes = [dict() for _ in range(self.num_opponents + 1)]

    ## Update knowledge of possible codes based on response from previous guess.
    def update(self, response):
        self.previous_responses.append(response)
        
    def get_next_guess(self):
        next_guess = ()
        start_time = time()

        ## Initial Guess
        ## ---------------------------------------------------------------------
        if len(self.previous_guesses) == 0:
            ## print("Initial Guess")
            next_guess = tuple(range(self.num_opponents))
            unused_weapons = tuple(range(self.num_opponents, self.num_weapons))
            
            for num_weps_correct in range(self.num_opponents + 1):
                for correct_weps in combinations(next_guess, num_weps_correct):
                    for wrong_weps in combinations(unused_weapons, self.num_opponents - num_weps_correct):
                        self.possible_codes[num_weps_correct][correct_weps + wrong_weps] = None

            counts = [len(self.possible_codes[i]) for i in range(self.num_opponents + 1)]
            sorted_index = sorted(range(self.num_opponents + 1), key=lambda k: counts[k], reverse=True)

            for num_weps_correct in sorted_index:
                for combo in self.possible_codes[num_weps_correct]:
                    if time() - start_time < 9:
                        self.possible_codes[num_weps_correct][combo] = set(permutations(combo))
                    else:
                        break
            
            self.previous_guesses.append(next_guess)
            ## print('Guess Time Taken: {} Seconds'.format(time() - start_time))
            return next_guess

        ## Update Possible Codes
        ## ---------------------------------------------------------------------
        prev_guess = self.previous_guesses[-1]
        num_weps_correct = self.previous_responses[-1][0]
        num_pos_correct = self.previous_responses[-1][1]

        ## First combination reduction is pre-computed
        if len(self.previous_guesses) == 1:
            self.possible_codes = self.possible_codes[num_weps_correct]
        ## Remove impossible combinations of weapons
        else:
            prev_guess_set = set(prev_guess)
            valid_combos = dict()
            for combo in self.possible_codes:
                count = 0
                for wep in combo:
                    if wep in prev_guess_set:
                        count += 1

                if count == num_weps_correct:
                    valid_combos[combo] = self.possible_codes[combo]

            self.possible_codes = valid_combos

        ## If the numper of weapon permutations is small enough to manage,
        ## compute permutations for all possible combinations.
        ## Remove impossible permutation of weapons.
        if len(self.possible_codes) * self.num_perm_per_combo < self.threshold:
            ## Cleaning time capped at 4 seconds to allocate time for guess selection.
            while time() - start_time < 4 and self.backlog < len(self.previous_guesses):
                prev_guess = self.previous_guesses[self.backlog]
                num_weps_correct = self.previous_responses[self.backlog][0]
                num_pos_correct = self.previous_responses[self.backlog][1]
                self.backlog += 1
                
                valid_combos = dict()
                for combo in self.possible_codes:
                    if self.possible_codes[combo] is None:
                        self.possible_codes[combo] = set(permutations(combo))

                    valid_perms = set()
                    for perms in self.possible_codes[combo]:
                        count = 0
                        for index in range(self.num_opponents):
                            if perms[index] == prev_guess[index]:
                                count += 1

                        if count == num_pos_correct:
                            valid_perms.add(perms)

                    if len(valid_perms) > 0:
                        valid_combos[combo] = valid_perms

                self.possible_codes = valid_combos
        
        ## Pick Next Guess
        ## ---------------------------------------------------------------------
                
        ## Only One Possible Code
        if len(self.possible_codes) == 1:
            all_possible_codes = [perm for perms in self.possible_codes.values() for perm in perms]
            if len(all_possible_codes) == 1:
                ## print("One Possible")
                ## print('Guess Time Taken: {} Seconds'.format(time() - start_time))
                return all_possible_codes[0]

        valid_weapons = set()
        for combo in self.possible_codes:
            valid_weapons.update(combo)

        temp = len(valid_weapons) + self.num_opponents - 1
        if temp < self.num_weapons:
            invalid_weapons = set(range(self.num_weapons)) - valid_weapons
            while len(valid_weapons) < temp:
                valid_weapons.add(invalid_weapons.pop())
        else:
            valid_weapons = set(range(self.num_weapons))
            
        ## Number of permutations is small enough to list
        if len(self.possible_codes) * self.num_perm_per_combo < self.threshold:
            all_possible_codes = [perm for perms in self.possible_codes.values() for perm in perms]
            best_worst_case = len(all_possible_codes) + 1
            
            ## Optimal Guess For Reducing Possible Weapon Permutations
            if len(all_possible_codes) * comb(len(valid_weapons), self.num_opponents) * self.num_perm_per_combo < self.threshold:
                ## print("Optimal")
                for guess in permutations(valid_weapons, self.num_opponents):
                    counter = [[0] * (self.num_opponents + 1) for _ in range(self.num_opponents + 1)]
                    guess_set = set(guess)
                    
                    for possible_code in all_possible_codes:
                        num_weps_correct = 0
                        num_pos_correct = 0
                        for i in range(self.num_opponents):
                            if possible_code[i] in guess_set:
                                num_weps_correct += 1
                                if possible_code[i] == guess[i]:
                                    num_pos_correct += 1

                        counter[num_weps_correct][num_pos_correct] += 1

                    worst_case = max([max(x) for x in counter])
                    if best_worst_case > worst_case:
                        next_guess = guess
                        best_worst_case = worst_case
                        if worst_case == 1:
                            break
                        
            ## Optimal Guess For Reducing Possible Weapon Permutations (Random Subsample)
            else:
                ## print("Optimal (Sample)")
                code_sample = sample(all_possible_codes, min(len(all_possible_codes), int(self.threshold / 100)))
                index = 0
    
                while time() - start_time < 9:
                    if len(code_sample) < 2000 and index < len(code_sample):
                        guess = code_sample[index]
                        index += 1
                    else:
                        guess = sample(valid_weapons, self.num_opponents)
                        shuffle(guess)
                        guess = tuple(guess)
                        
                    guess_set = set(guess)
                    counter = [[0] * (self.num_opponents + 1) for _ in range(self.num_opponents + 1)]
                    
                    for possible_code in code_sample:
                        num_weps_correct = 0
                        num_pos_correct = 0
                        for i in range(self.num_opponents):
                            if possible_code[i] in guess_set:
                                num_weps_correct += 1
                                if possible_code[i] == guess[i]:
                                    num_pos_correct += 1

                        counter[num_weps_correct][num_pos_correct] += 1

                    worst_case = max([max(x) for x in counter])
                    if best_worst_case > worst_case:
                        next_guess = guess
                        best_worst_case = worst_case
                        if worst_case == 1:
                            break
                        
        ## Optimal Guess For Reducing Possible Weapon Combinations (Random Subsample)
        else:
            ## print("Approx. (Sample)")
            all_possible_combos = self.possible_codes.keys()
            best_worst_case = len(all_possible_combos)
            
            combo_sample = list(combinations(valid_weapons, self.num_opponents))
            shuffle(combo_sample)

            for guess in combo_sample:
                guess = list(guess)
                shuffle(guess)
                guess = tuple(guess)
                
                counter = [0] * (self.num_opponents + 1)
                guess_set = set(guess)

                for possible_combo in all_possible_combos:
                    num_weps_correct = 0
                    for i in range(self.num_opponents):
                        if possible_combo[i] in guess_set:
                            num_weps_correct += 1

                    counter[num_weps_correct] += 1

                worst_case = max(counter)
                if best_worst_case > worst_case:
                    next_guess = guess
                    best_worst_case = worst_case

                if time() - start_time > 9:
                    break
                
        self.previous_guesses.append(next_guess)
        ## print('Guess Time Taken: {} Seconds'.format(time() - start_time))
        return next_guess
