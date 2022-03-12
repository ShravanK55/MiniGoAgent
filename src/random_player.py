import random
from read import readInput
from write import writeOutput

from host import GO

class RandomPlayer():
    """
    A Go agent that plays by performing random valid moves.
    """

    def __init__(self):
        """
        Method to initialize the random agent.
        """
        self.type = "random"

    def get_agent_action(self, go, piece_type):
        """
        Method to get the agent action.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').

        Returns:
            (row, column): Co-ordinates of the board to place the agent's piece at. Returns "PASS" instead if no valid
                placement is possible.

        """
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = RandomPlayer()
    action = player.get_agent_action(go, piece_type)
    writeOutput(action)