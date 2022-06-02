import requests
import base64
import json
import zlib
from itertools import permutations, combinations_with_replacement

## Globals
email   = 'johnsmith@email.com'
##email   = input("Enter your email address: ")
baseURL = "http://crypto.praetorian.com"

r = requests.post('{url}/api-token-auth/'.format(url=baseURL), data={'email':email})
auth_token = r.json()['token']
r.close()

headers = {'Authorization':"JWT {}".format(auth_token)}
hashes = {}


## -----------------------------------------------------------------------------
## Communication Code

## Save hash to '{email}_hashes.txt' if avalible
def save_hashes():
    global hashes
    print("Saving hashes to " + email + "_hashes.txt")
    with open(email + "_hashes.txt", "w") as f:
        f.write("Email: {}\n".format(email))
        f.write("Hashes:\n")
        for i in range(len(hashes)):
            f.write("  {}: {}\n".format(i, hashes[i]))

## Get challenge data and hint
def get_challenge(level_num):
    global baseURL, headers
    url = '{url}/challenge/{level_num}/'
    requestURL = url.format(url=baseURL, level_num=level_num)
    response = requests.get(requestURL, headers=headers)
    response.close()
    
    if response.status_code != 200:
        raise Exception(response.json()['detail'])

    return response.json()

## Send a guess
def submit_guess(level_num, guess):
    global baseURL, headers
    url = '{url}/challenge/{level_num}/'
    requestURL = url.format(url=baseURL, level_num=level_num)
    response = requests.post(requestURL, headers=headers, data={'guess':guess})
    response.close()

    if response.status_code != 200:
        raise Exception(response.json()['detail'])

    if 'hash' in response.json():
        hashes[level_num] = response.json()['hash']
        return True

    return False

## Challenge data is flag
def solve_level_0(data):
    flag = data['challenge']
    
    if submit_guess(0, flag):
        return flag

    raise Exception("Failed Level 0".format(flag))

## Caesar Cipher
def solve_level_1(data):
    cipher = data['challenge']
    flag = ''

    for char in cipher:
        if (char.isupper()):
            flag += chr((ord(char) + 3 - 65) % 26 + 65)
        else:
            flag += chr((ord(char) + 3 - 97) % 26 + 97)

    if submit_guess(1, flag):
        return flag
    
    raise Exception("Failed Level 1: {}".format(flag))

## Flag is hidden in the HCKR chunk.
def solve_level_2(data):
    png = base64.b64decode(data['challenge'].split(',')[1])
    index = png.find(b'HCKR') + 4
    flag = ''

    while png[index] < 128 and chr(png[index]).isalpha():
        flag += chr(png[index])
        index += 1

    ## Sometime the bytes following the flag happen to be ascii letters.
    original_flag = flag
    while not submit_guess(2, flag):
        flag = flag[:-1]
        if len(flag) == 0:
            raise Exception("Failed Level 2: {}".format(original_flag))

    return flag

## Steganography
## Letters of the code are disguised as pixel values in the PNG.
def solve_level_3(data):
    png = base64.b64decode(data['challenge'].split(',')[1])
    start = png.find(b'IDAT') + 4
    end = png.find(b'IEND')
    pixels = zlib.decompress(png[start:end])
    caps_count = 0

    flag = ''

    for byte in pixels:
        if byte < 128 and chr(byte).isalpha():
            if chr(byte).isupper():
                caps_count += 1
            if caps_count == 4:
                break
            flag += chr(byte)

    if submit_guess(3, flag):
        return flag

    raise Exception("Failed Level 3: {}".format(flag))

## Obfuscation
## Due to the small hash output space 2^16 we can brute force a collision.
def solve_level_4(data):
    password_hash = int(data['challenge'].split()[-1], 16)
    flag = ''

    ## Unobfuscated hash function
    def hash_func(password):
        _hash = 0xBEEF

        for i, byte in enumerate(password):
            _hash = _hash ^ (byte * 0xBABE) ^ (0xFACE * i)
            _hash = _hash & 0xFFFF
        
        return _hash

    alphabet = [ord(c) for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ']

    for i in range(1, 6):
        combos = combinations_with_replacement(alphabet, i)
        for combo in combos:
            perms = permutations(combo, i)
            for perm in perms:
                if hash_func(perm) == password_hash:
                    flag = ''.join([chr(n) for n in perm])
                    if submit_guess(4, flag):
                        return flag
                    raise Exception("Failed Level 4: {}".format(flag))
    
    raise Exception("Failed Level 4: {}".format(flag))

## ----------------------------------------------------------------------------------------------
## Play the game
    
if __name__ == '__main__':
    solvers = [solve_level_0, solve_level_1, solve_level_2, solve_level_3, solve_level_4]
    
    for level_num, solver in enumerate(solvers):
        data = get_challenge(level_num)
        flag = solver(data)
        print('Level {} Flag: {}'.format(level_num, flag))

    print()
    print("Level Hashes")
    for k in hashes:
        print("{}: {}".format(k, hashes[k]))

    print()
    save_hashes()




    
