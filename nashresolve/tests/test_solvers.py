from typing import cast
from unittest import TestCase, main

from nashresolve.contrib.poker import KuhnPokerTreeFactory
from nashresolve.contrib.rockpaperscissors import RockPaperScissorsTreeFactory
from nashresolve.contrib.tictactoe import TicTacToeTreeFactory
from nashresolve.solvers import CFRPSolver, CFRSolver, DCFRSolver, TreeSolver
from nashresolve.trees import ChanceNode, Node, PlayerNode, TerminalNode


class TreeSolverTestCase(TestCase):
    def verify(self, solver: TreeSolver) -> None:
        self.verify_node(solver.game.root, solver)

    def verify_node(self, node: Node, solver: TreeSolver) -> None:
        if isinstance(node, ChanceNode):
            self.assertAlmostEqual(sum(node.probabilities), 1)
        elif isinstance(node, PlayerNode):
            self.assertAlmostEqual(sum(solver.query(node.info_set)), 1)

        for child in node.children:
            self.verify_node(child, solver)

    KUHN_POKER_ITER_COUNT = 100
    KUHN_POKER_GAME = KuhnPokerTreeFactory().build()

    def test_kuhn_poker_cfr(self) -> None:
        solver = CFRSolver(self.KUHN_POKER_GAME)

        for i in range(self.KUHN_POKER_ITER_COUNT):
            solver.step()

        self.verify_kuhn_poker(solver, 1)

    def test_kuhn_poker_cfrp(self) -> None:
        solver = CFRPSolver(self.KUHN_POKER_GAME)

        for i in range(self.KUHN_POKER_ITER_COUNT):
            solver.step()

        self.verify_kuhn_poker(solver, 2)

    def test_kuhn_poker_dcfr(self) -> None:
        solver = DCFRSolver(self.KUHN_POKER_GAME)

        for i in range(self.KUHN_POKER_ITER_COUNT):
            solver.step()

        self.verify_kuhn_poker(solver, 3)

    def verify_kuhn_poker(self, solver: TreeSolver, places: int) -> None:
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

    Tic_Tac_Toe_ITER_COUNT = 5
    Tic_Tac_Toe_GAME = TicTacToeTreeFactory().build()

    def test_tic_tac_toe_cfr(self) -> None:
        solver = CFRSolver(self.Tic_Tac_Toe_GAME)

        for i in range(self.Tic_Tac_Toe_ITER_COUNT):
            solver.step()

        self.verify_tic_tac_toe(solver)

    def test_tic_tac_toe_cfrp(self) -> None:
        solver = CFRPSolver(self.Tic_Tac_Toe_GAME)

        for i in range(self.Tic_Tac_Toe_ITER_COUNT):
            solver.step()

        self.verify_tic_tac_toe(solver)

    def test_tic_tac_toe_dcfr(self) -> None:
        solver = DCFRSolver(self.Tic_Tac_Toe_GAME)

        for i in range(self.Tic_Tac_Toe_ITER_COUNT):
            solver.step()

        self.verify_tic_tac_toe(solver)

    def verify_tic_tac_toe(self, solver: TreeSolver) -> None:
        self.verify(solver)

        query = solver.query(cast(PlayerNode, self.Tic_Tac_Toe_GAME.root).info_set)

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

        node = self.Tic_Tac_Toe_GAME.root
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

    ROCK_PAPER_SCISSORS_ITER_COUNT = 100
    ROCK_PAPER_SCISSORS_GAME = RockPaperScissorsTreeFactory().build()

    def test_rock_paper_scissors_cfr(self) -> None:
        solver = CFRSolver(self.ROCK_PAPER_SCISSORS_GAME)

        for i in range(self.ROCK_PAPER_SCISSORS_ITER_COUNT):
            solver.step()

        for info_set in self.ROCK_PAPER_SCISSORS_GAME.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)

    def test_rock_paper_scissors_cfrp(self) -> None:
        solver = CFRPSolver(self.ROCK_PAPER_SCISSORS_GAME)

        for i in range(self.ROCK_PAPER_SCISSORS_ITER_COUNT):
            solver.step()

        for info_set in self.ROCK_PAPER_SCISSORS_GAME.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)

    def test_rock_paper_scissors_dcfr(self) -> None:
        solver = DCFRSolver(self.ROCK_PAPER_SCISSORS_GAME)

        for i in range(self.ROCK_PAPER_SCISSORS_ITER_COUNT):
            solver.step()

    def verify_rock_paper_scissors(self, solver: TreeSolver) -> None:
        self.verify(solver)

        for info_set in self.ROCK_PAPER_SCISSORS_GAME.info_sets:
            for value in solver.query(info_set):
                self.assertAlmostEqual(value, 1 / 3)


if __name__ == '__main__':
    main()
