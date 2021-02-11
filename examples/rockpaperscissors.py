from time import time

from nashresolve.rockpaperscissors import RPSTreeFactory
from nashresolve.solvers import CFRSolver
from nashresolve.utils import interact_tree_game

game = RPSTreeFactory().build()
solver = CFRSolver(game)
iter_count = 1000

print('Starting...')

start_time = time()

for i in range(iter_count):
    print(solver.step())

print(f'Took: {time() - start_time}')

interact_tree_game(game, solver)
