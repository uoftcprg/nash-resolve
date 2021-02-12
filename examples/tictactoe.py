import pickle
from os import path
from time import time

from nashresolve.contrib.tictactoe import TTTTreeFactory as Factory  # VAR
from nashresolve.solvers import DCFRSolver as Solver  # VAR
from utils import interact_tree_game

FILE_NAME = 'tictactoe-dcfr.nrs'  # VAR
ITER_COUNT = 100  # VAR

print('Starting...')

if path.exists(FILE_NAME):
    print('Loading existing solver...')

    with open(FILE_NAME, 'rb') as file:
        solver = pickle.load(file)
else:
    print('Constructing tree...')

    solver = Solver(Factory().build())

print('Solving...')

start_time = time()

for i in range(ITER_COUNT):
    print(f'Iteration {i}:', ' '.join(map(str, solver.step())))

print(f'Took: {time() - start_time} s')
print('EV:', ' '.join(map(str, solver.ev())))

with open(FILE_NAME, 'wb') as file:
    pickle.dump(solver, file)

interact_tree_game(solver.game, solver)
