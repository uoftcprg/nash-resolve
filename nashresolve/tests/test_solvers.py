from unittest import TestCase, main

from nashresolve.rockpaperscissors import RPSTreeFactory
from nashresolve.solvers import CFRSolver


class SolverTestCase(TestCase):
    RPS_ITER_COUNT = 10

    def test_rps(self) -> None:
        game = RPSTreeFactory().build()
        solver = CFRSolver(game)

        for i in range(self.RPS_ITER_COUNT):
            solver.step()

        for info_set in game.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)


if __name__ == '__main__':
    main()
