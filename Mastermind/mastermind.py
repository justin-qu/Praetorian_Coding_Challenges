import requests
import json
import time
import sys

from gladiator import Gladiator

## Constants
##email   = 'johnsmith@email.com'
email   = input("Enter your email address: ")
baseURL = 'https://mastermind.praetorian.com'

r = requests.post('{url}/api-auth-token/'.format(url=baseURL), data={'email':email})
auth_token = r.json()['Auth-Token']
headers = {'Content-Type':'application/json', 'Auth-Token':auth_token}

## Globals
level_num = 1

## -----------------------------------------------------------------------------
## Communication Code

## Resets game back to level 1
def reset_levels():
    global baseURL, headers
    url = '{url}/reset/'
    requestURL = url.format(url=baseURL)
    r = requests.post(requestURL, headers=headers)
    response = r.json()

    if 'error' in response:
        raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response['error']))

## Save hash to '{email}_hash.txt' if avalible
def get_hash(hashString):
    print("Saving hash to " + email + "_hash.txt")
    with open(email + "_hash.txt", "w") as f:
        f.write("Email: " + email +  "\nHash: " + hashString)
    sys.exit()

## Start level 'num'
## Return level parameters
def start_level():
    global baseURL, headers, level_num
    url = '{url}/level/{level_num}'
    requestURL = url.format(url=baseURL, level_num=level_num)
    r = requests.get(requestURL, headers=headers)
    response = r.json()

    if 'error' in response:
        if response['error'] == 'Requested level cannot yet be challenged, complete lower levels first.':
            print("Failed to start level " + str(level_num))
            print("Restarting level " + str(level_num - 1))
            level_num -= 1
            return start_level()
        else:
            raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response['error']))

    return response

## Send a guess
## Return response
def send_guess(guess):
    global baseURL, headers, level_num
    url = '{url}/level/{level_num}/'
    requestURL = url.format(url=baseURL, level_num=level_num)
    r = requests.post(requestURL, headers=headers, data=json.dumps({'guess':list(guess)}))
    response = r.json()
    
    return response

## ----------------------------------------------------------------------------------------------
## Play the game
    
if __name__ == '__main__':
    reset_levels()
    print()

    while level_num < 7:
        print("Starting level " + str(level_num))
        level_params = start_level()
        print(level_params)
        hercules = Gladiator(level_params['numWeapons'], level_params['numGladiators'])
        break_all = False
        
        for i in range(level_params['numRounds']):
            print('Round: ' + str(i+1))
            for _ in range(level_params['numGuesses']):
                response = send_guess(hercules.get_next_guess())
                if 'roundsLeft' in response:
                    hercules.reset()
                    break
                elif 'hash' in response:
                    get_hash(response['hash'])
                    break_all = True
                elif 'message' in response:
                    break
                elif 'error' in response:
                    if response['error'] == 'Too many guesses. Try again!':
                        break_all = True
                        break
                    else:
                        raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response['error']))
                else:
                    hercules.update(response['response'])

            if break_all:
                break

        print("Level " + str(level_num) + " finished\n")
        level_num += 1
