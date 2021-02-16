import pickle
from os import path
from time import time

from nashresolve.contrib.onecardpoker import OCPTreeFactory
from nashresolve.solvers import CFRSolver
from utils import interact_tree_game

PLAYER_COUNT = 2
STACK = 5
FILE_NAME = f'onecardpoker-{PLAYER_COUNT}-{STACK}-dcfr.nrs'
ITER_COUNT = 0

print('Starting...')

if path.exists(FILE_NAME):
    print('Loading existing solver...')

    with open(FILE_NAME, 'rb') as file:
        solver = pickle.load(file)
else:
    print('Constructing tree...')

    solver = CFRSolver(OCPTreeFactory(1, [1, 2], [STACK] * PLAYER_COUNT).build())

print('Solving...')

start_time = time()

for i in range(ITER_COUNT):
    print(f'Iteration {i}:', ' '.join(map(str, solver.step())))

print(f'Took: {time() - start_time} s')
print('EV:', ' '.join(map(str, solver.ev())))

with open(FILE_NAME, 'wb') as file:
    pickle.dump(solver, file)

print(len(solver.game.info_sets))

interact_tree_game(solver.game, solver)
