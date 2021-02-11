import pickle
from time import time

from nashresolve.tictactoe import TTTTreeFactory
from nashresolve.solvers import CFRSolver
from nashresolve.utils import interact_tree_game
from os import path

FILE_NAME = 'tictactoe-cfr.nrs'
ITER_COUNT = 50
SAVE_INTERVAL = 100

print('Starting...')

if path.exists(FILE_NAME):
    print('Loading existing solver...')

    with open(FILE_NAME, 'rb') as file:
        solver = pickle.load(file)
else:
    print('Constructing tree...')

    solver = CFRSolver(TTTTreeFactory().build())

print('Solving...')

start_time = time()

for i in range(ITER_COUNT):
    print(f'Iteration {i}:', ' '.join(map(str, solver.step())))

    if i % SAVE_INTERVAL == 0:
        with open(FILE_NAME, 'wb') as file:
            pickle.dump(solver, file)
else:
    with open(FILE_NAME, 'wb') as file:
        pickle.dump(solver, file)

print(f'Took: {time() - start_time} s')
print('EV:', ' '.join(map(str, solver.ev())))

interact_tree_game(solver.game, solver)
