import requests
import json
import time
import sys

from gameState import GameState

##email   = 'johnsmith@email.com'
email   = input("Enter your email address: ")
baseURL = 'http://rota.praetorian.com/rota/service/play.php?request='
cookie  = None

## -----------------------------------------------------------------------------
## Communication code

## Start a new game.
## Resets win streak.
def new_game():
    global email, baseURL, cookie
    url = '{url}new&email={email}'
    requestURL = url.format(url=baseURL, email=email)
    r = requests.get(requestURL)
    response = r.json()
    cookie = r.cookies

    if response['status'] == 'success':
        return response['data']['board']

    raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response))

## Place a piece in position x.
def place(x: int):
    global email, baseURL, cookie
    url = '{url}place&location={location}'
    requestURL = url.format(url=baseURL, location=x)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        return response['data']['board']

    raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response))

## Move a piece in position x to position y.
def move(x: int, y: int):
    global email, baseURL, cookie
    url = '{url}move&from={oldLocation}&to={newLocation}'
    requestURL = url.format(url=baseURL, oldLocation=x, newLocation=y)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        return response['data']['moves'], response['data']['board']

    raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response))

## Check game status.
## Returns current board state.
def status():
    global email, baseURL, cookie
    url = '{url}status&email={email}'
    requestURL = url.format(url=baseURL, email=email)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        return response['data']

    raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response))

## Start next game.
## If sufficient games won, save hash to file.
def next_game():
    global email, baseURL, cookie
    url = '{url}next'
    requestURL = url.format(url=baseURL)
    r = requests.get(requestURL, cookies=cookie)
    response = r.json()

    if response['status'] == 'success':
        if 'hash' in response['data']:
            get_hash(response['data']['hash'])
        else:
            return response['data']['games_won'], response['data']['board']

    raise ValueError("HTTP GET Request Failed.\n{}\n{}\n".format(requestURL, response))

def get_hash(hashString):
    print("Saving hash to " + email + "_hash.txt")
    with open(email + "_hash.txt", "w") as f:
        f.write("Email: " + email +  "\nHash: " + hashString)
    sys.exit()

##------------------------------------------------------------------------------------------
## Play the game
    
if __name__ == '__main__':
    player = GameState()
    state = new_game()
    numMoves = 0
    numGames = 0
    startTime = time.time()

    ## Play games until hash recieved (challenge requires 50 games)
    while True:
        print('Game Number: {}'.format(numGames))

        ## Make moves until game is over (games requires you make 30 moves without losing.)
        while numMoves < 30:
    ##        print(str(state[0]) + str(state[1]) + str(state[2]))
    ##        print(str(state[3]) + str(state[4]) + str(state[5]))
    ##        print(str(state[6]) + str(state[7]) + str(state[8]))
    ##        print('\n')
            
            next_move = player.get_next_move(state)

            if len(next_move) == 1:
                state = place(next_move[0])
            else:
                numMoves, state = move(next_move[0], next_move[1])

        print('Time Elapsed: {0:3f}'.format(time.time() - startTime))
        numGames, state = next_game()
        numMoves = 0
