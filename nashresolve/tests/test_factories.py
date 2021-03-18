from unittest import TestCase, main

from nashresolve.contrib.rockpaperscissors import RockPaperScissorsTreeFactory
from nashresolve.trees import TerminalNode


class FactoryTestCase(TestCase):
    def test_rock_paper_scissors(self) -> None:
        game = RockPaperScissorsTreeFactory().build()

        self.assertEqual(len(set(game.nodes)), 13)
        self.assertEqual(len(set(game.info_sets)), 2)
        self.assertEqual(len(game.root.children), 3)

        for child in game.root.children:
            self.assertEqual(len(child.children), 3)

        for grandchild, payoffs in zip(sum((child.children for child in game.root.children), start=tuple()),
                                       [[0, 0], [-1, 1], [1, -1], [1, -1], [0, 0], [-1, 1], [-1, 1], [1, -1], [0, 0]]):
            if isinstance(grandchild, TerminalNode):
                self.assertSequenceEqual(grandchild.payoffs, payoffs)
            else:
                self.fail()


if __name__ == '__main__':
    main()
