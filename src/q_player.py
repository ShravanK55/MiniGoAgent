import copy
import json
import random
from read import readInput
from utils import get_rotated_state, get_flipped_state, get_equivalent_action
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
        self.updated_q_values = {}

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
            (q_values, equiv_state, h_flipped, v_flipped, num_rotations): Q values for the given Go board state, the
                equivalent state, whether the state was horizontally flipped, whether the state was vertically flipped,
                and the number of rotations to find the equivalent action.

        """
        equiv_state, h_flipped, v_flipped, num_rot = self.get_equivalent_state(state)

        if equiv_state is None:
            equiv_state = state
            self.q_values[state] = [[self.default_q_value for _ in range(self.board_size)] for _ in
                                    range(self.board_size)]

        return self.q_values[equiv_state], equiv_state, h_flipped, v_flipped, num_rot


    def get_equivalent_state(self, state):
        """
        Method to get a state in the Q values which is symmetrically and rotationally equivalent to the given state.

        Args:
            state(str): State to get the rotational and symmetric equivalent for.

        Returns:
            (equivalent_state, flip_horizontal, flip_vertical, rotation_amount): The equivalent state, whether the
                original state is flipped horizontally, whether the original state was flipped vertically, number of
                clockwise rotations to find the equivalent action.

        """
        # Check rotated states without symmetry.
        rotated_state, num_rotations = self.get_equivalent_rotated_state(state)
        if rotated_state is not None:
            return (rotated_state, False, False, num_rotations)

        # Check states with horizontal symmetry.
        hf_state = get_flipped_state(state, self.board_size, True, False)
        hf_r_state, num_rotations = self.get_equivalent_rotated_state(hf_state)
        if hf_r_state is not None:
            return (hf_r_state, True, False, num_rotations)

        # Check states with vertical symmetry.
        vf_state = get_flipped_state(state, self.board_size, False, True)
        vf_r_state, num_rotations = self.get_equivalent_rotated_state(vf_state)
        if vf_r_state is not None:
            return (vf_r_state, False, True, num_rotations)

        # Check states with horizontal and vertical symmetry.
        hvf_state = get_flipped_state(state, self.board_size, True, True)
        hvf_r_state, num_rotations = self.get_equivalent_rotated_state(hvf_state)
        if hvf_r_state is not None:
            return (hvf_r_state, True, True, num_rotations)

        return (None, False, False, 0)


    def get_equivalent_rotated_state(self, state):
        """
        Method to get a state in the Q values which is rotationally equivalent to the given state.

        Args:
            state(str): State to get the rotationa equivalent for.

        Returns:
            (equivalent_state, rotation_amount): The equivalent state and the number of clockwise rotations to find the
                equivalent action.

        """
        if state in self.q_values:
            return (state, 0)

        state_r1 = get_rotated_state(state, self.board_size)
        if state_r1 in self.q_values:
            return (state_r1, 3)

        state_r2 = get_rotated_state(state_r1, self.board_size)
        if state_r2 in self.q_values:
            return (state_r2, 2)

        state_r3 = get_rotated_state(state_r2, self.board_size)
        if state_r3 in self.q_values:
            return (state_r3, 1)

        return (None, 0)


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

            q_values, equiv_state, h_flipped, v_flipped, num_rot = self.q(state)
            self.updated_q_values[equiv_state] = q_values

            # Rotate action in the same way as equivalent state.
            num_rot = 4 - num_rot if num_rot > 0 else num_rot
            e_action = get_equivalent_action(action, self.board_size, h_flipped, v_flipped, num_rot, False)

            if max_q_value < 0:
                q_values[e_action[0]][e_action[1]] = round(reward, 4)
            else:
                q_values[e_action[0]][e_action[1]] = round((1 - self.alpha) * q_values[e_action[0]][e_action[1]] +
                                                           self.alpha * self.gamma * max_q_value, 4)

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

        action, value = self.get_max_action(go, piece_type)
        self.state_history.append((go.encoded_state, action))
        return action


    def get_max_action(self, go, piece_type):
        """
        Method to get the action with the maximum Q value for a given state.

        Args:
            go(GO): Instance of the Go board.
            piece_type(int): Type of piece the player agent is playing as. 1('X') or 2('O').

        Returns:
            (action, value): Action with the maximum Q value.

        """
        max_actions = ["PASS"]
        max_q = float("-inf")

        q_values, _, h_flipped, v_flipped, num_rot = self.q(go.encoded_state)
        for i in range(go.size):
            for j in range(go.size):
                if q_values[i][j] >= max_q:
                    equiv_action = get_equivalent_action((i, j), self.board_size, h_flipped, v_flipped, num_rot)
                    if go.valid_place_check(equiv_action[0], equiv_action[1], piece_type, test_check=True):
                        if q_values[i][j] > max_q:
                            max_actions = [equiv_action]
                            max_q = q_values[i][j]
                        else:
                            max_actions.append(equiv_action)

                    else:
                        q_values[i][j] = -1.0


        max_action = max_actions[0]
        if len(max_actions) > 1:
            max_action = random.choice(max_actions)

        return max_action, max_q


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)

    player = QPlayer(piece_type, Q_TABLE_PATH)
    action = player.get_agent_action(go, piece_type)
    writeOutput(action)
