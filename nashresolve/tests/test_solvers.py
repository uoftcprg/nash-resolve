from unittest import TestCase, main

from nashresolve.contrib.rockpaperscissors import RPSTreeFactory
from nashresolve.solvers import CFRPSolver, CFRSolver, DCFRSolver


class SolverTestCase(TestCase):
    RPS_CFR_ITER_COUNT = 20
    RPS_CFRP_ITER_COUNT = 20
    RPS_DCFR_ITER_COUNT = 20

    def test_rps_cfr(self) -> None:
        game = RPSTreeFactory().build()
        solver = CFRSolver(game)

        for i in range(self.RPS_CFR_ITER_COUNT):
            solver.step()

        for info_set in game.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)

    def test_rps_cfrp(self) -> None:
        game = RPSTreeFactory().build()
        solver = CFRPSolver(game)

        for i in range(self.RPS_CFRP_ITER_COUNT):
            solver.step()

        for info_set in game.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)

    def test_rps_dcfr(self) -> None:
        game = RPSTreeFactory().build()
        solver = DCFRSolver(game)

        for i in range(self.RPS_DCFR_ITER_COUNT):
            solver.step()

        for info_set in game.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)


if __name__ == '__main__':
    main()
