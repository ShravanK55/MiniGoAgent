import time

from alpha_beta_player import AlphaBetaPlayer
from q_player import QPlayer
from read import readInput
from write import writeOutput

from host import GO


TURN_FILE = "turn_number.txt"


if __name__ == "__main__":
    player_type = "ALPHA_BETA"
    N = 5
    MAX_DEPTH = 3
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)

    turn_number = 1
    with open(TURN_FILE, 'r') as turn_file:
        turn_number = int(turn_file.readlines()[0])

    actual_turn = turn_number * 2 - 1 if piece_type == 1 else turn_number * 2
    depth = MAX_DEPTH if go.max_move - actual_turn + 1 >= MAX_DEPTH else go.max_move - actual_turn + 1
    print("Turn: {}. Depth: {}".format(actual_turn, depth))

    action = "PASS"
    start = time.time()
    if board[int(N / 2)][int(N / 2)] == 0 and actual_turn <= 2:
        action = (2, 2)
    elif player_type == "ALPHA_BETA":
        player = AlphaBetaPlayer()
        action = player.get_agent_action(go, piece_type, depth)
    elif player_type == "Q":
        player = QPlayer(piece_type, "q_values.json")
        action = player.get_agent_action(go, piece_type)
    end = time.time()
    print("Time taken: {}".format(end - start))

    writeOutput(action)

    with open(TURN_FILE, 'w') as turn_file:
        if (actual_turn + 2 > go.max_move):
            turn_file.write(str(1))
        else:
            turn_file.write(str(turn_number + 1))

    actual_turn = turn_number * 2 - 1
