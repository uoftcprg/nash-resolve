from typing import Optional, Sequence, cast

from nashresolve.games import TreeGame
from nashresolve.solvers import TreeSolver
from nashresolve.trees import ChanceNode, NonTerminalNode, PlayerNode, TerminalNode


def interact_tree_game(game: TreeGame, solver: Optional[TreeSolver] = None) -> None:
    node = game.root

    while isinstance(node, NonTerminalNode):
        print(f'Current: {node}\nChildren:')

        probabilities: Sequence[Optional[float]]

        if solver is not None and isinstance(node, PlayerNode):
            probabilities = solver.query(node.info_set)
        elif isinstance(node, ChanceNode):
            probabilities = node.probabilities
        else:
            probabilities = [None] * len(node.children)

        for i, (child, probability) in enumerate(zip(node.children, probabilities)):
            if probability is None:
                print(f'Child {i}: {child}')
            else:
                print(f'Child {i}: {child} ({probability})')

        node = node.children[int(input('Choice: '))]

    print(f'Current: {node}')
    print('Payoffs:', ' '.join(map(str, cast(TerminalNode, node).payoffs)))
