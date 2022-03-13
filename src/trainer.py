import json
from copy import deepcopy
from random import Random
from host import GO
from alpha_beta_player import AlphaBetaPlayer
from random_player import RandomPlayer
from q_player import QPlayer


Q_TABLE_PATH = "q_values.json"


def train(go, player1, player2, q_table_path="q_values.json", save_results=False):
    """
    Method to train a Q learning agent by playing a series of games against another player.

    Args:
        go(GO): Instance of the Go board.
        player1(GoPlayer): Instance of player 1 agent.
        player2(GoPlayer): Instance of player 2 agent.
        q_table_path(str): Path to the Q table file. Defaults to "q_values.json".
        save_results(bool): Whether to save the updated Q values after every game. Defaults to False.

    Returns:
        (winner): Winner of the game.

    """
    go.init_board(go.size)

    #if player1.type == "q-learner" or player2.type == "q-learner":
    #    go.verbose = True
    #    go.visualize_board()

    x_move = True
    verbose = False # go.verbose
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

            if (player1.type == "q-learner"):
                player1.learn(result)
            if (player2.type == "q-learner"):
                player2.learn(result)

            if save_results:
                q_values = {}
                if player1.type == "q-learner" and player2.type == "q-learner":
                    q_values.update(player1.q_values)
                    q_values.update(player2.updated_q_values)
                elif player1.type == "q-learner":
                    q_values = player1.q_values
                elif player2.type == "q-learner":
                    q_values = player2.q_values

                if q_values:
                    with open(q_table_path, 'w') as q_values_file:
                        json.dump(q_values, q_values_file)

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
    MAX_BATCHES = 2

    for i in range(MAX_BATCHES):
        print("BATCH: {}".format(i))
        MAX_GAMES = 1000
        num_games = 0

        q_path = Q_TABLE_PATH
        piece_type = 1
        player1 = QPlayer(piece_type, q_path)
        player2 = QPlayer(3 - piece_type, q_path)
        switch_sides = player2.type != "q-learner"
        p1_wins = 0
        p2_wins = 0
        draws = 0

        while num_games < MAX_GAMES:
            print("Game Number: {}.".format(i * MAX_GAMES + num_games))
            N = 5
            go = GO(N)

            result = train(go, player1, player2, q_path)
            num_games += 1

            if result == 1:
                p1_wins += 1
            elif result == 2:
                p2_wins += 1
            else:
                draws += 1

            if switch_sides:
                piece_type = 3 - piece_type
                player1, player2 = player2, player1

                if player1.type == "q-learner":
                    player1.set_piece_type(piece_type)

                if player2.type == "q-learner":
                    player2.set_piece_type(piece_type)

        print("P1 Wins: {}. P2 Wins: {}. Draws: {}".format(p1_wins, p2_wins, draws))

        q_values = {}
        if player1.type == "q-learner" and player2.type == "q-learner":
            q_values.update(player1.q_values)
            q_values.update(player2.updated_q_values)
        elif player1.type == "q-learner":
            q_values = player1.q_values
        elif player2.type == "q-learner":
            q_values = player2.q_values

        if q_values:
            with open(q_path, 'w') as q_values_file:
                json.dump(q_values, q_values_file)
