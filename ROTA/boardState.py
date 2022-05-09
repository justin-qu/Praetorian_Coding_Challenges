## Defines a state of the board
##
## Empty Space : 0
## Player 1    : 1
## player 2    : -1
##
## BoardState.center = X
## BoardState.state = (a,b,c,d,e,f,g,h)
##
## a b c
## h X d
## g f e
##
## BoardState.winner[(x, y)]: If True, player x will win if it is player y's turn
## BoardState.pieceCount: Count of each piece
## BoardState.gameOver: If True, a player has won the game (three-in-a-row)

class BoardState:
    def __init__(self, center, state):
        self.center = center
        self.state = state

        self.nextStates = [None, set(), set()]

        ## (Player Winner, Player Turn)
        self.winner = dict()
        self.winner[(1, 1)]   = False
        self.winner[(1, -1)]  = False
        self.winner[(-1, 1)]  = False
        self.winner[(-1, -1)] = False

        self.pieceCount = [0, 0, 0]
        self.pieceCount[1], self.pieceCount[-1] = self._num_pieces()

        self.is_game_over = False
        self._is_game_over()

    ## Check if state is a terminal state (three-in-a-row)
    ## If so, set gameOver to True
    def _is_game_over(self):
        center = self.center
        state = list(self.state)
        state.extend(state[:2])

        ## Check for three-in-a-row around the ring
        for i in range(8):
            if state[i] != 0 and state[i] == state[i+1] and state[i] == state[i+2]:
                self.winner[(state[i], -state[i])] = True
                self.is_game_over = True

        ## Check for three-in-a-row through the center
        if center != 0:
            for i in range(4):
                if center == state[i] and center == state[i+4]:
                    self.winner[(state[i], -state[i])] = True
                    self.is_game_over = True

    ## Count number of each pieces in state
    def _num_pieces(self):
        count = [0,0,0]
        count[self.center] += 1

        for i in self.state:
            count[i] += 1
            
        ## (Player 1 (1), Player 2 (-1))
        return (count[1], count[2])

    def __str__(self):
        s = "{} {} {}\n{} {} {}\n{} {} {}"
        state  = self.state
        center = self.center
        s.format(state[0], state[1], state[2],
                 state[7], center,   state[3],
                 state[6], state[5], state[4])

        return s
        
