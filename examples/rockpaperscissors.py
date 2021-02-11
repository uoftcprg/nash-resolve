from time import time

from nashresolve.rockpaperscissors import RPSTreeFactory
from nashresolve.solvers import CFRSolver
from utils import interact_tree_game

game = RPSTreeFactory().build()
solver = CFRSolver(game)
iter_count = 100

print('Starting...')

start_time = time()

for i in range(iter_count):
    print(solver.step())

print(f'Took: {time() - start_time}')

interact_tree_game(game, solver)
