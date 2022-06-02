# Praetorian Challenge: Mastermind

### Dependencies
* Python Version: 3.6
* Python 'requests' module

This code is for the [Praetorian Mastermind Challenge](https://www.praetorian.com/challenges/mastermind).

### File Summaries
* __mastermind.py__ is the main script that will complete the challenge.
* __gladiator.py__ contains the logic used to determine the best next guess and which codes are still possible.
* __gladiatorTest.py__ contains code used to simulate a level and debug __gladiator.py__.

### How To Use
1. Run __mastermind.py__.

### Algorithms
The primary guessing algorithm used in the logic is a variation of [Kunth's Mastermind Algorithm](https://en.wikipedia.org/wiki/Mastermind_(board_game)#Worst_case:_Five-guess_algorithm) (KMA). 
Gladiator.py contains various different approximations of KMA depending on the size of the search space in order to make a reasoned guess within the time limit.

These approximations include:
* Randomly selecting a subset of all possible permutations and running KMA over the subset to approximate the larger set.
* If the number of permutations is too large, we apply these concepts to combinations (rather than permutations) in an effort to reduce the number of possible combinations.

Deduction primarily involves removing permutations/combinations from lists/sets if a guess is checked against the permutation/combination and the simulated response does not match the response given by the server.