from collections import defaultdict
from functools import partial
from unittest import TestCase, main

from nashresolve import KuhnPokerTreeFactory, RockPaperScissorsTreeFactory, TerminalNode, TicTacToeTreeFactory


class FactoryTestCase(TestCase):
    def test_rock_paper_scissors(self):
        for player_count in range(2, 6):
            game = RockPaperScissorsTreeFactory(player_count).build()

            self.assertEqual(game.player_count, player_count)
            self.assertEqual(len(tuple(game.nodes)), sum(map(partial(pow, 3), range(player_count + 1))))
            self.assertEqual(len(tuple(game.terminal_nodes)), 3 ** player_count)
            self.assertEqual(len(tuple(game.chance_nodes)), 0)
            self.assertEqual(len(tuple(game.player_nodes)), sum(map(partial(pow, 3), range(player_count))))
            self.assertEqual(len(set(game.info_sets)), player_count)

            if player_count == 2:
                self.assertTrue(game.is_zero_sum())

                frequencies = defaultdict(int)

                for payoffs in map(TerminalNode.payoffs.fget, game.terminal_nodes):
                    frequencies[tuple(payoffs)] += 1

                self.assertSetEqual(set(frequencies.keys()), {(0, 0), (-1, 1), (1, -1)})
                self.assertSequenceEqual(tuple(frequencies.values()), (3, 3, 3))
            else:
                self.assertFalse(game.is_zero_sum())

            for player_node in game.player_nodes:
                self.assertEqual(len(tuple(player_node.children)), 3)

    def test_tic_tac_toe(self):
        game = TicTacToeTreeFactory().build()

        self.assertEqual(game.player_count, 2)
        self.assertEqual(len(tuple(game.nodes)), 549946)
        self.assertEqual(len(tuple(game.terminal_nodes)), 255168)
        self.assertEqual(len(tuple(game.chance_nodes)), 0)
        self.assertEqual(len(tuple(game.player_nodes)), 294778)
        self.assertEqual(len(set(game.info_sets)), 4520)
        self.assertTrue(game.is_zero_sum())

        self.assertSetEqual(
            set(map(tuple, map(TerminalNode.payoffs.fget, game.terminal_nodes))),
            {(0, 0), (-1, 1), (1, -1)},
        )

    def test_kuhn(self):
        game = KuhnPokerTreeFactory().build()

        self.assertEqual(game.player_count, 2)
        self.assertEqual(len(tuple(game.nodes)), 58)
        self.assertEqual(len(tuple(game.terminal_nodes)), 30)
        self.assertEqual(len(tuple(game.chance_nodes)), 4)
        self.assertEqual(len(tuple(game.player_nodes)), 24)
        self.assertEqual(len(set(game.info_sets)), 12)
        self.assertTrue(game.is_zero_sum())

        self.assertSetEqual(
            set(map(tuple, map(TerminalNode.payoffs.fget, game.terminal_nodes))),
            {(-1, 1), (1, -1), (2, -2), (-2, 2)},
        )


if __name__ == '__main__':
    main()
