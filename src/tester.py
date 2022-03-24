import json
from copy import deepcopy
from host import GO
from alpha_beta_player import AlphaBetaPlayer
from random_player import RandomPlayer


def play(go, player1, player2):
    """
    Method to train a Q learning agent by playing a series of games against another player.

    Args:
        go(GO): Instance of the Go board.
        player1(GoPlayer): Instance of player 1 agent.
        player2(GoPlayer): Instance of player 2 agent.

    Returns:
        (winner): Winner of the game.

    """
    go.init_board(go.size)

    x_move = True
    verbose = False
    # Game starts!
    while 1:
        piece_type = 1 if x_move else 2

        # Judge if the game should end
        if go.game_end(piece_type):
            result = go.judge_winner()
            if verbose:
                print('Game ended.')
                if result == 0:
                    print('The game is a tie.')
                else:
                    print('The winner is {}'.format('X' if result == 1 else 'O'))

            return result

        if verbose:
            player = "X" if piece_type == 1 else "O"
            print(player + " makes move...")

        # Game continues
        if piece_type == 1: action = player1.get_agent_action(go, piece_type)
        else: action = player2.get_agent_action(go, piece_type)

        if verbose:
            player = "X" if piece_type == 1 else "O"
            print(action)

        if action != "PASS":
            # If invalid input, continue the loop. Else it places a chess on the board.
            if not go.place_chess(action[0], action[1], piece_type):
                if verbose:
                    go.visualize_board()
                continue

            go.died_pieces = go.remove_died_pieces(3 - piece_type) # Remove the dead pieces of opponent
        else:
            go.previous_board = deepcopy(go.board)

        if verbose:
            go.visualize_board() # Visualize the board again
            print()

        go.n_move += 1
        x_move = not x_move # Players take turn


if __name__ == "__main__":
    MAX_BATCHES = 5

    for i in range(MAX_BATCHES):
        print("BATCH: {}".format(i))
        MAX_GAMES = 100
        num_games = 0

        piece_type = 1
        player1 = AlphaBetaPlayer()
        player2 = RandomPlayer()
        switch_sides = True
        p1_wins = 0
        p2_wins = 0
        draws = 0

        while num_games < MAX_GAMES:
            print("Game Number: {}.".format(i * MAX_GAMES + num_games))
            N = 5
            go = GO(N)

            result = play(go, player1, player2)
            num_games += 1

            if result == piece_type:
                p1_wins += 1
            elif result == 3 - piece_type:
                p2_wins += 1
            else:
                draws += 1

            if switch_sides:
                piece_type = 3 - piece_type
                player1, player2 = player2, player1

        print("P1 Wins: {}. P2 Wins: {}. Draws: {}".format(p1_wins, p2_wins, draws))
