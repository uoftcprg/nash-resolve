from typing import cast
from unittest import TestCase, main

from nashresolve.contrib.onecardpoker import OCPTreeFactory
from nashresolve.contrib.rockpaperscissors import RPSTreeFactory
from nashresolve.contrib.tictactoe import TTTTreeFactory
from nashresolve.solvers import CFRPSolver, CFRSolver, DCFRSolver, TreeSolver
from nashresolve.trees import ChanceNode, Node, NonTerminalNode, PlayerNode, TerminalNode


class SolverTestCase(TestCase):
    def verify(self, solver: TreeSolver) -> None:
        self.verify_aux(solver.game.root, solver)

    def verify_aux(self, node: Node, solver: TreeSolver) -> None:
        if isinstance(node, ChanceNode):
            self.assertAlmostEqual(sum(node.probabilities), 1)
        elif isinstance(node, PlayerNode):
            self.assertAlmostEqual(sum(solver.query(node.info_set)), 1)

        if isinstance(node, NonTerminalNode):
            for child in node.children:
                self.verify_aux(child, solver)

    OCP_ITER_COUNT = 50
    OCP_GAME = OCPTreeFactory(1, [1, 2], [5, 5]).build()

    def test_ocp_cfr(self) -> None:
        solver = CFRSolver(self.OCP_GAME)

        for i in range(self.OCP_ITER_COUNT):
            solver.step()

        self.verify_ocp(solver, 1)

    def test_ocp_cfrp(self) -> None:
        solver = CFRPSolver(self.OCP_GAME)

        for i in range(self.OCP_ITER_COUNT):
            solver.step()

        self.verify_ocp(solver, 2)

    def test_ocp_dcfr(self) -> None:
        solver = DCFRSolver(self.OCP_GAME)

        for i in range(self.OCP_ITER_COUNT):
            solver.step()

        self.verify_ocp(solver, 4)

    def verify_ocp(self, solver: TreeSolver, places: int) -> None:
        self.verify(solver)

        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[1].children[0]).info_set)[1], 0, places)
        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[1].children[0].children[2]).info_set)[1], 0, places)
        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[11].children[11]).info_set)[0], 0, places)
        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[12].children[11].children[2]).info_set)[0], 0, places)
        self.assertAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[12].children[11].children[1]).info_set)[0], 0, places)
        self.assertNotAlmostEqual(solver.query(
            cast(PlayerNode, solver.game.root.children[11].children[11]).info_set)[1], 0, places)

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

        self.assertAlmostEqual(query[0], query[2])
        self.assertAlmostEqual(query[2], query[6])
        self.assertAlmostEqual(query[6], query[8])

        self.assertAlmostEqual(query[1], query[3])
        self.assertAlmostEqual(query[3], query[5])
        self.assertAlmostEqual(query[5], query[7])

        self.assertGreater(query[0], query[1])
        self.assertGreater(query[4], query[1])

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
