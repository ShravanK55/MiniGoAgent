import copy
from read import readInput
from write import writeOutput

from host import GO


class QPlayer():
    """
    Module that implements an agent that plays a miniature version of Go using the Q-learning algorithm.
    """

    def get_agent_action(self, go, piece_type):
        """
        Method to get the action to be performed by the agent. Uses the Q-learning algorithm to get the optimal action.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').

        Returns:
            (row, column): Co-ordinates of the board to place the agent's piece at. Returns "PASS" instead if no valid
                placement is possible.

        """
        action, value = self.max_action(go, piece_type, max_depth, float("-inf"), float("inf"))
        print("Player performs action {} with value {}".format(action, value))

        return action


    def get_reward_value(self, go, piece_type, dead_pieces_player=0, dead_pieces_opp=0):
        """
        Method to get the reward value of the board for a given piece type.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').

        Returns:
            (value): Utility value for the state of the Go board from the perspective of the player.

        """
        # Base score is the number of pieces on the board for each player.
        player_score = go.score(piece_type)
        opponent_score = go.score(3 - piece_type)

        # Additional score where amount of liberty for each pawn group is added to the utility value.
        player_liberty_score = 0
        opponent_liberty_score = 0
        visited = [[False for _ in range(go.size)] for _ in range(go.size)]

        for i in range(go.size):
            for j in range(go.size):
                if not visited[i][j] and go.board[i][j] != 0:
                    allies = go.ally_dfs(i, j)
                    for ally in allies:
                        visited[ally[0]][ally[1]] = True
                        neighbours = go.detect_neighbor(ally[0], ally[1])

                        for neighbour in neighbours:
                            if go.board[neighbour[0]][neighbour[1]] == 0:
                                if go.board[ally[0]][ally[1]] == piece_type:
                                    player_liberty_score += 1
                                else:
                                    opponent_liberty_score += 1

        # If the player is white, add the komi value to the player score, else add it to the opponent's score.
        return player_score + player_liberty_score + go.komi - (opponent_score + opponent_liberty_score) \
               if piece_type == 2 else \
               player_score + player_liberty_score - (opponent_score + opponent_liberty_score + go.komi)


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = QPlayer()
    action = player.get_agent_action(go, piece_type, 3)
    writeOutput(action)
