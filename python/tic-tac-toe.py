
from collections import namedtuple

State = namedtuple('State', ['G', 'ctx'])
GameOver = namedtuple('GameOver', ['winner', 'draw'])
Context = namedtuple('Context', ['gameover'])

class TicTacToe:

    def setup():
        return [None]*9

    def observation(G):
        return list(map(lambda c: 0 if c is None else int(c)+1, G))

    def enumerate(G):
        r = []
        for i in range(len(G)):
            if G[i] is None:
                r.append(i)
        return r
    
    positions = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]

    def is_victory(G):
        for pos in TicTacToe.positions:
            symbol = G[pos[0]]
            winner = symbol
            for i in pos:
                if G[i] != symbol:
                    winner = None
                    break
            if winner != None:
                return True
        return False
        
    
    def step(G, ctx, action, playerID):
        G[action] = playerID
        if TicTacToe.is_victory(G):
            ctx = Context(GameOver(playerID, False))
        if None not in G:
            ctx = Context(GameOver(None, True))
        return State(G, ctx)
        

    name = 'tic-tac-toe'

    action_space = [0, 8]
    observation_space = [9, 3]
