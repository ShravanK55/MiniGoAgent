import json
from read import readInput
from write import writeOutput

from host import GO


Q_TABLE_PATH = "q_values.json"

WIN_REWARD = 1
DRAW_REWARD = 0.5
LOSS_REWARD = 0


class QPlayer():
    """
    Module that implements an agent that plays a miniature version of Go using the Q-learning algorithm.
    """

    def __init__(self, piece_type, q_table_path=Q_TABLE_PATH, alpha=0.7, gamma=0.9, default_q_value=0.5, board_size=5):
        """
        Method to initialize the Q-learning player.

        Args:
            piece_type(int): Piece type of the player. 1 -> Black, 2 -> White.
            q_table_path(str): Path to the Q table file. Defaults to "q_values.json".
            alpha(float): Learning rate for the Q learning algorithm. Defaults to 0.7.
            gamma(float): Discount value for future rewards. Defaults to 0.9.
            default_q_value(float): Default Q value to use when we explore a new state. Defaults to 0.5.
            board_size(int): Size of the Go board. Defaults to 5.

        """
        self.type = "q-learner"
        self.piece_type = piece_type
        self.alpha = alpha
        self.gamma = gamma
        self.q_values = {}

        with open(q_table_path, 'r') as q_values_file:
            self.q_values = json.load(q_values_file)

        self.state_history = []
        self.default_q_value = default_q_value
        self.board_size = board_size


    def set_piece_type(self, piece_type):
        """
        Method to set the piece type of the Q player.

        Args:
            piece_type(int): Piece type of the player. 1 -> Black, 2 -> White.

        """
        self.piece_type = piece_type


    def dump_values(self, q_table_path="q_values.json"):
        """
        Method to dump the learned Q values into a JSON file.

        Args:
            q_table_path(str): Path to dump the Q values on to. Defaults to "q_values.json".

        """
        with open(q_table_path, 'w') as q_values_file:
            json.dump(self.q_values, q_values_file)


    def q(self, state):
        """
        Method to get the Q values for a given Go state.

        Args:
            state(str): Encoded state of the Go board.

        Returns:
            (q_values): Q values for the given Go board state.

        """
        if state not in self.q_values:
            self.q_values[state] = [[self.default_q_value for _ in range(self.board_size)] for _ in
                                    range(self.board_size)]

        return self.q_values[state]


    def learn(self, result):
        """
        Method to update the Q values of the agent by learning from the game proceedings.

        Args:
            result(int): Result of the game. 0 -> Draw, 1 -> Black wins, 2 -> White wins.

        """
        reward = 0
        if result == 0:
            reward = DRAW_REWARD
        elif result == self.piece_type:
            reward = WIN_REWARD
        else:
            reward = LOSS_REWARD

        self.state_history.reverse()
        max_q_value = -1

        for state, action in self.state_history:
            if action == "PASS":
                continue

            q_values = self.q(state)
            if max_q_value < 0:
                q_values[action[0]][action[1]] = reward
            else:
                q_values[action[0]][action[1]] = (1 - self.alpha) * q_values[action[0]][action[1]] + \
                                                 self.alpha * self.gamma * max_q_value

            for i in range(self.board_size):
                for j in range(self.board_size):
                    if q_values[i][j] > max_q_value:
                        max_q_value = q_values[i][j]

        self.state_history = []


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
        q_values = self.q(go.encoded_state)
        action, value = self.get_max_action(go, piece_type, q_values)

        print("Player performs action {} with value {}".format(action, value))
        self.state_history.append((go.encoded_state, action))
        return action


    def get_max_action(self, go, piece_type, q_values):
        """
        Method to get the action with the maximum Q value for a given state.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').
            q_values(list): Q values for the actions that can be performed in the given state.

        Returns:
            (action, value): Action with the maximum Q value.

        """
        max_action = "PASS"
        max_q = float("-inf")

        for i in range(go.size):
            for j in range(go.size):
                if q_values[i][j] > max_q:
                    if go.valid_place_check(i, j, piece_type, test_check=True):
                        max_action = (i, j)
                        max_q = q_values[i][j]

                    else:
                        q_values[i][j] = -1.0

        return max_action, max_q


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)

    player = QPlayer(piece_type, Q_TABLE_PATH)
    action = player.get_agent_action(go, piece_type)
    writeOutput(action)
