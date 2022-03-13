import copy
from read import readInput
from write import writeOutput

from host import GO


class AlphaBetaPlayer():
    def __init__(self):
        self.type = 'alpha-beta'

    def get_agent_action(self, go, piece_type, max_depth=3):
        """
        Method to get the action to be performed by the agent. Uses the alpha-beta pruning algorithm to get the optimal
        action (depth-limited).

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').
            max_depth(int): Max steps to look ahead in the game state tree for. Defaults to 3.

        Returns:
            (row, column): Co-ordinates of the board to place the agent's piece at. Returns "PASS" instead if no valid
                placement is possible.

        """
        action, _ = self.max_action(go, piece_type, max_depth, float("-inf"), float("inf"))

        return action


    def get_utility_value(self, go, piece_type):
        """
        Method to get the utility value of the board for a given piece type.

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
        visited = [[False for x in range(go.size)] for y in range(go.size)]

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


    def max_action(self, go, piece_type, depth=0, alpha=float("-inf"), beta=float("inf")):
        """
        Method to get the action that maximizes the reward for a piece type.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').
            depth(int): Number of steps to look ahead in the game state tree for. Defaults to 0.
            alpha(float): Alpha value used in the alpha-beta pruning algorithm. Defaults to float("-inf").
            beta(float): Beta value used in the alpha-beta pruning algorithm. Defaults to float("-inf").

        Returns:
            ((row, column), value): Action and utility value for board when the action is executed.

        """
        if (depth == 0):
            return "PASS", self.get_utility_value(go, piece_type)

        # Getting the possible actions for the agent.
        actions = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    actions.append((i,j))

        # If no valid action exists, simply pass.
        if not actions:
            return "PASS", self.get_utility_value(go, piece_type)

        # Run the minimax recursion with alpha-beta pruning.
        a = "PASS"
        v = float("-inf")
        for action in actions:
            test_go = copy.deepcopy(go)
            test_go.place_chess(action[0], action[1], piece_type)
            test_go.remove_died_pieces(3 - piece_type)

            _, action_value = self.min_action(test_go, piece_type, depth - 1, alpha, beta)

            a = action if action_value > v else a
            v = max(v, action_value)

            if (v >= beta):
                return a, v

            alpha = max(alpha, v)

        return a, v


    def min_action(self, go, piece_type, depth=0, alpha=float("-inf"), beta=float("inf")):
        """
        Method to get the action that minimizes the reward for the opponent piece type.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').
            depth(int): Number of steps to look ahead in the game state tree for. Defaults to 0.
            alpha(float): Alpha value used in the alpha-beta pruning algorithm. Defaults to float("-inf").
            beta(float): Beta value used in the alpha-beta pruning algorithm. Defaults to float("-inf").

        Returns:
            ((row, column), value): Action and utility value for board when the action is executed.

        """
        if (depth == 0):
            return "PASS", self.get_utility_value(go, piece_type)

        # Getting the possible actions for the opponent agent.
        actions = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, 3 - piece_type, test_check = True):
                    actions.append((i,j))

        # If no valid action exists, simply pass.
        if not actions:
            return "PASS", self.get_utility_value(go, piece_type)

        # Run the minimax recursion with alpha-beta pruning.
        a = "PASS"
        v = float("inf")
        for action in actions:
            test_go = copy.deepcopy(go)
            test_go.place_chess(action[0], action[1], 3 - piece_type)
            test_go.remove_died_pieces(piece_type)

            _, action_value = self.max_action(test_go, piece_type, depth - 1, alpha, beta)

            a = action if action_value > v else a
            v = min(v, action_value)

            if (v <= alpha):
                return a, v

            beta = min(beta, v)

        return a, v


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = AlphaBetaPlayer()
    action = player.get_agent_action(go, piece_type, 3)
    writeOutput(action)
