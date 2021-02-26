from typing import cast
from unittest import TestCase, main

from nashresolve.contrib.poker import KuhnTreeFactory
from nashresolve.contrib.rockpaperscissors import RPSTreeFactory
from nashresolve.contrib.tictactoe import TTTTreeFactory
from nashresolve.solvers import CFRPSolver, CFRSolver, DCFRSolver, TreeSolver
from nashresolve.trees import ChanceNode, Node, NonTerminalNode, PlayerNode, TerminalNode


class TreeSolverTestCase(TestCase):
    def verify(self, solver: TreeSolver) -> None:
        self.verify_node(solver.game.root, solver)

    def verify_node(self, node: Node, solver: TreeSolver) -> None:
        if isinstance(node, ChanceNode):
            self.assertAlmostEqual(sum(node.probabilities), 1)
        elif isinstance(node, PlayerNode):
            self.assertAlmostEqual(sum(solver.query(node.info_set)), 1)

        if isinstance(node, NonTerminalNode):
            for child in node.children:
                self.verify_node(child, solver)

    KUHN_ITER_COUNT = 100
    KUHN_GAME = KuhnTreeFactory().build()

    def test_kuhn_cfr(self) -> None:
        solver = CFRSolver(self.KUHN_GAME)

        for i in range(self.KUHN_ITER_COUNT):
            solver.step()

        self.verify_kuhn(solver, 1)

    def test_kuhn_cfrp(self) -> None:
        solver = CFRPSolver(self.KUHN_GAME)

        for i in range(self.KUHN_ITER_COUNT):
            solver.step()

        self.verify_kuhn(solver, 2)

    def test_kuhn_dcfr(self) -> None:
        solver = DCFRSolver(self.KUHN_GAME)

        for i in range(self.KUHN_ITER_COUNT):
            solver.step()

        self.verify_kuhn(solver, 3)

    def verify_kuhn(self, solver: TreeSolver, places: int) -> None:
        self.verify(solver)

        # Check obvious strategy

        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[1].children[0]).info_set)[0], 1, places)
        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[1].children[0].children[1]).info_set)[0], 1, places)
        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[0].children[0].children[0]).info_set)[0], 1, places)

        # Check mixed strategy

        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[2].children[1]).info_set)[0], 0, places)
        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[2].children[1]).info_set)[0], 1, places)
        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[2].children[1].children[1]).info_set)[0], 0, places)
        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[2].children[1].children[1]).info_set)[1], 0, places)
        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[0].children[0]).info_set)[0], 0, places)
        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[0].children[0]).info_set)[1], 0, places)

    TTT_ITER_COUNT = 5
    TTT_GAME = TTTTreeFactory().build()

    def test_ttt_cfr(self) -> None:
        solver = CFRSolver(self.TTT_GAME)

        for i in range(self.TTT_ITER_COUNT):
            solver.step()

        self.verify_ttt(solver)

    def test_ttt_cfrp(self) -> None:
        solver = CFRPSolver(self.TTT_GAME)

        for i in range(self.TTT_ITER_COUNT):
            solver.step()

        self.verify_ttt(solver)

    def test_ttt_dcfr(self) -> None:
        solver = DCFRSolver(self.TTT_GAME)

        for i in range(self.TTT_ITER_COUNT):
            solver.step()

        self.verify_ttt(solver)

    def verify_ttt(self, solver: TreeSolver) -> None:
        self.verify(solver)

        query = solver.query(cast(PlayerNode, self.TTT_GAME.root).info_set)

        # Check symmetry

        self.assertAlmostEqual(query[0], query[2])
        self.assertAlmostEqual(query[2], query[6])
        self.assertAlmostEqual(query[6], query[8])

        self.assertAlmostEqual(query[1], query[3])
        self.assertAlmostEqual(query[3], query[5])
        self.assertAlmostEqual(query[5], query[7])

        self.assertGreater(query[0], query[1])
        self.assertGreater(query[4], query[1])

        # Check optimal strategy leading to tie

        node = self.TTT_GAME.root
        count = 0

        while not isinstance(node, TerminalNode):
            node = cast(PlayerNode, node)
            self.assertEqual(len(node.children), 9 - count)

            strategy = solver.query(node.info_set)
            node = node.children[max(range(len(node.children)), key=lambda i: strategy[i])]
            count += 1
        else:
            self.assertAlmostEqual(node.payoffs[0], 0)
            self.assertAlmostEqual(node.payoffs[1], 0)
            self.assertEqual(count, 9)

    RPS_ITER_COUNT = 100
    RPS_GAME = RPSTreeFactory().build()

    def test_rps_cfr(self) -> None:
        solver = CFRSolver(self.RPS_GAME)

        for i in range(self.RPS_ITER_COUNT):
            solver.step()

        for info_set in self.RPS_GAME.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)

    def test_rps_cfrp(self) -> None:
        solver = CFRPSolver(self.RPS_GAME)

        for i in range(self.RPS_ITER_COUNT):
            solver.step()

        for info_set in self.RPS_GAME.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)

    def test_rps_dcfr(self) -> None:
        solver = DCFRSolver(self.RPS_GAME)

        for i in range(self.RPS_ITER_COUNT):
            solver.step()

    def verify_rps(self, solver: TreeSolver) -> None:
        self.verify(solver)

        for info_set in self.RPS_GAME.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)


if __name__ == '__main__':
    main()
