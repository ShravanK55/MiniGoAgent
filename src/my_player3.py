from alpha_beta_player import AlphaBetaPlayer
from q_player import QPlayer
from read import readInput
from write import writeOutput

from host import GO


if __name__ == "__main__":
    player_type = "ALPHA_BETA"
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)

    action = "PASS"
    if player_type == "ALPHA_BETA":
        player = AlphaBetaPlayer()
        action = player.get_agent_action(go, piece_type, 3)
    elif player_type == "Q":
        player = QPlayer()
        action = player.get_agent_action(go, piece_type)

    writeOutput(action)
